from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import date, timedelta
from pathlib import PurePath
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import log_event, pseudonymous_reference
from app.core.security import create_access_token, hash_password, verify_password
from app.data_exchange import build_csv_export, build_json_export, parse_csv_import
from app.db import SessionLocal
from app.deps import current_user
from app.migrations import database_initialisation_lock, run_migrations
from app.models import Goal, ImportJob, TrainingSet, User, Workout
from app.notifications import send_goal_completed_notification
from app.repositories import SqlAlchemySkillTrackRepository, get_repository
from app.schemas import DashboardOut, GoalIn, GoalOut, LoginIn, Token, UserOut, WorkoutIn, WorkoutOut
from app.services import create_workout, dashboard, make_workout_out, update_workout

API_VERSION = "1.1.0"
MAX_CSV_BYTES = 2_000_000
API_CONTENT_SECURITY_POLICY = (
    "default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
)
DOCUMENTATION_CONTENT_SECURITY_POLICY = (
    "default-src 'none'; "
    "base-uri 'none'; "
    "form-action 'none'; "
    "frame-ancestors 'none'; "
    "connect-src 'self'; "
    "script-src 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
    "font-src https://fonts.gstatic.com; "
    "img-src data: https://fastapi.tiangolo.com"
)
logger = logging.getLogger("skilltrack.api")


def seed_demo_data(db: Session, user: User) -> None:
    base = date.today()
    examples = [
        (
            "Planche technique",
            "Planche",
            7,
            [("Tuck planche hold", 0, 0, 20, 7), ("Pseudo planche push-up", 8, 0, 0, 8)],
        ),
        (
            "Front lever contrôle",
            "Pull",
            6,
            [("Advanced tuck front lever", 0, 0, 25, 6), ("Tractions tempo", 6, 10, 0, 7)],
        ),
        (
            "Force poussée",
            "Push",
            8,
            [("Dips lestés", 5, 40, 0, 8), ("Handstand push-up", 4, 0, 0, 7)],
        ),
    ]
    for i, (title, workout_type, intensity, training_sets) in enumerate(examples):
        workout = Workout(
            owner_id=user.id,
            title=title,
            date=base - timedelta(days=i * 3),
            type=workout_type,
            intensity=intensity,
            duration_minutes=75,
            notes="Données de démonstration",
        )
        for exercise, reps, load, duration, difficulty in training_sets:
            workout.sets.append(
                TrainingSet(
                    exercise=exercise,
                    category="autre",
                    set_count=1,
                    reps=reps,
                    load_kg=load,
                    duration_seconds=duration,
                    difficulty=difficulty,
                    assistance_kg=0,
                    notes="",
                )
            )
        db.add(workout)
    db.add_all(
        [
            Goal(
                owner_id=user.id,
                skill="Full planche",
                target="Tenir 5 secondes propre",
                current_level="Straddle / full courte",
                deadline=base + timedelta(days=90),
            ),
            Goal(
                owner_id=user.id,
                skill="Front lever",
                target="20 secondes propres",
                current_level="Avancé",
                deadline=base + timedelta(days=60),
            ),
            Goal(
                owner_id=user.id,
                skill="HSPU",
                target="10 répétitions strictes",
                current_level="6-8 reps",
                deadline=base + timedelta(days=45),
            ),
            Goal(
                owner_id=user.id,
                skill="Handstand",
                target="Tenir 30 secondes",
                current_level="30 secondes",
                current_value=30,
                target_value=30,
                unit="secondes",
                status="termine",
                is_done=True,
            ),
        ]
    )
    db.commit()


def initialise_database() -> None:
    with database_initialisation_lock():
        run_migrations()
        db = SessionLocal()
        try:
            repository = SqlAlchemySkillTrackRepository(db)
            user = repository.user_by_email(settings.demo_email)
            created_demo_user = user is None
            if not user:
                user = User(
                    email=settings.demo_email,
                    display_name="Demo",
                    password_hash=hash_password(settings.demo_password),
                )
                repository.add(user)
                repository.commit()
                repository.refresh(user)
            # Seed only a newly created demo account. A restart must never
            # resurrect records that the user deliberately edited or deleted.
            if created_demo_user:
                seed_demo_data(db, user)
        finally:
            db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialise_database()
    yield


app = FastAPI(title="SkillTrack API", version=API_VERSION, lifespan=lifespan)
documentation_paths = {
    path
    for path in (app.docs_url, app.redoc_url, app.swagger_ui_oauth2_redirect_url)
    if path is not None
}
origins = [origin.strip() for origin in settings.backend_cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    request_id = str(uuid4())
    try:
        response = await call_next(request)
    except Exception as exc:
        route = request.scope.get("route")
        route_path = getattr(route, "path", "unmatched")
        log_event(
            logger,
            logging.ERROR,
            "unhandled_request_error",
            request_id=request_id,
            method=request.method,
            route=route_path,
            error_type=type(exc).__name__,
        )
        raise
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        DOCUMENTATION_CONTENT_SECURITY_POLICY
        if request.url.path in documentation_paths
        else API_CONTENT_SECURITY_POLICY
    )
    response.headers["Cache-Control"] = "no-store"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if response.status_code >= 400:
        route = request.scope.get("route")
        log_event(
            logger,
            logging.WARNING,
            "request_error",
            request_id=request_id,
            method=request.method,
            route=getattr(route, "path", "unmatched"),
            status_code=response.status_code,
        )
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "SkillTrack"}


@app.post("/auth/login", response_model=Token)
def login(
    data: LoginIn,
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
) -> Token:
    user = repository.user_by_email(data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Identifiants invalides")
    return Token(access_token=create_access_token(user.id))


@app.get("/users/me", response_model=UserOut)
def me(user: User = Depends(current_user)) -> User:
    return user


@app.get("/dashboard", response_model=DashboardOut)
def get_dashboard(
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> dict:
    return dashboard(repository, user)


@app.get("/workouts", response_model=list[WorkoutOut])
def list_workouts(
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> list[dict]:
    workouts = repository.workouts_for_owner(user.id)
    return [make_workout_out(workout) for workout in workouts]


@app.post("/workouts", response_model=WorkoutOut)
def post_workout(
    data: WorkoutIn,
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> dict:
    return make_workout_out(create_workout(repository, user, data))


def _owned_workout(repository: SqlAlchemySkillTrackRepository, user: User, workout_id: str) -> Workout:
    workout = repository.workout_for_owner(user.id, workout_id)
    if not workout:
        raise HTTPException(404, "Séance introuvable")
    return workout


@app.get("/workouts/{workout_id}", response_model=WorkoutOut)
def get_workout(
    workout_id: str,
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> dict:
    return make_workout_out(_owned_workout(repository, user, workout_id))


@app.put("/workouts/{workout_id}", response_model=WorkoutOut)
def put_workout(
    workout_id: str,
    data: WorkoutIn,
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> dict:
    return make_workout_out(
        update_workout(repository, _owned_workout(repository, user, workout_id), data)
    )


@app.delete("/workouts/{workout_id}")
def delete_workout(
    workout_id: str,
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> dict[str, bool]:
    workout = _owned_workout(repository, user, workout_id)
    repository.delete(workout)
    repository.commit()
    return {"deleted": True}


@app.get("/goals", response_model=list[GoalOut])
def list_goals(
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> list[Goal]:
    return repository.goals_for_owner(user.id)


@app.post("/goals", response_model=GoalOut)
def add_goal(
    data: GoalIn,
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> Goal:
    goal = Goal(owner_id=user.id, **data.model_dump())
    repository.add(goal)
    repository.commit()
    repository.refresh(goal)
    return goal


@app.put("/goals/{goal_id}", response_model=GoalOut)
def edit_goal(
    goal_id: str,
    data: GoalIn,
    background_tasks: BackgroundTasks,
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> Goal:
    goal = repository.goal_for_owner(user.id, goal_id)
    if not goal:
        raise HTTPException(404, "Objectif introuvable")
    was_completed = goal.status == "termine"
    for key, value in data.model_dump().items():
        setattr(goal, key, value)
    repository.commit()
    repository.refresh(goal)
    if not was_completed and goal.status == "termine":
        background_tasks.add_task(
            send_goal_completed_notification,
            user.email,
            user.display_name,
            goal.skill,
        )
    return goal


@app.delete("/goals/{goal_id}")
def remove_goal(
    goal_id: str,
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> dict[str, bool]:
    goal = repository.goal_for_owner(user.id, goal_id)
    if not goal:
        raise HTTPException(404, "Objectif introuvable")
    repository.delete(goal)
    repository.commit()
    return {"deleted": True}


def _safe_filename(filename: str | None) -> str:
    normalised = (filename or "import.csv").replace("\\", "/")
    basename = PurePath(normalised).name or "import.csv"
    if len(basename) <= 255:
        return basename
    stem, dot, suffix = basename.rpartition(".")
    extension = f".{suffix}" if dot else ""
    return f"{(stem or basename)[: 255 - len(extension)]}{extension}"


@app.post("/imports/csv")
def import_csv(
    file: UploadFile = File(...),
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> dict:
    filename = _safe_filename(file.filename)
    if not filename.lower().endswith(".csv"):
        raise HTTPException(415, "Le fichier doit être au format CSV.")
    raw = file.file.read(MAX_CSV_BYTES + 1)
    if len(raw) > MAX_CSV_BYTES:
        raise HTTPException(413, "Le fichier CSV dépasse la limite de 2 Mo.")
    try:
        decoded = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(422, "Le fichier doit être encodé en UTF-8.") from exc
    try:
        plan = parse_csv_import(decoded)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

    objects: list[Workout | Goal | ImportJob] = []
    for data in plan.workouts:
        workout = Workout(owner_id=user.id, **data.model_dump(exclude={"sets"}))
        workout.sets.extend(TrainingSet(**training_set.model_dump()) for training_set in data.sets)
        objects.append(workout)
    objects.extend(Goal(owner_id=user.id, **data.model_dump()) for data in plan.goals)
    job = ImportJob(
        owner_id=user.id,
        filename=filename,
        imported_rows=plan.imported_rows,
        rejected_rows=plan.rejected_rows,
        ignored_rows=plan.ignored_rows,
        report="\n".join(plan.errors),
    )
    objects.append(job)
    try:
        repository.add_all(objects)
        repository.commit()
        repository.refresh(job)
    except SQLAlchemyError as exc:
        repository.rollback()
        log_event(
            logger,
            logging.ERROR,
            "csv_import",
            status="rolled_back",
            owner_ref=pseudonymous_reference(user.id),
            error_type=type(exc).__name__,
        )
        raise HTTPException(500, "L'import a échoué : aucune donnée n'a été enregistrée.") from exc

    status = "completed"
    if plan.rejected_rows and plan.imported_rows:
        status = "completed_with_errors"
    elif plan.rejected_rows:
        status = "rejected"
    log_event(
        logger,
        logging.INFO,
        "csv_import",
        status=status,
        owner_ref=pseudonymous_reference(user.id),
        imported_rows=plan.imported_rows,
        rejected_rows=plan.rejected_rows,
        ignored_rows=plan.ignored_rows,
    )
    return {
        "id": job.id,
        "import_id": job.id,
        "status": status,
        "imported_rows": plan.imported_rows,
        "rejected_rows": plan.rejected_rows,
        "ignored_rows": plan.ignored_rows,
        "created_workouts": len(plan.workouts),
        "created_goals": len(plan.goals),
        "errors": plan.errors,
    }


@app.get("/imports/history")
def import_history(
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> list[dict]:
    jobs = repository.imports_for_owner(user.id, limit=20)
    return [
        {
            "id": job.id,
            "filename": job.filename,
            "imported_rows": job.imported_rows,
            "rejected_rows": job.rejected_rows,
            "ignored_rows": job.ignored_rows,
            "errors": job.report.splitlines() if job.report else [],
            "created_at": job.created_at,
        }
        for job in jobs
    ]


@app.delete("/imports/history/{job_id}")
def delete_import_history(
    job_id: str,
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> dict[str, bool]:
    job = repository.import_for_owner(user.id, job_id)
    if not job:
        raise HTTPException(404, "Historique d'import introuvable")
    repository.delete(job)
    repository.commit()
    log_event(
        logger,
        logging.INFO,
        "csv_import_history_deletion",
        status="completed",
        owner_ref=pseudonymous_reference(user.id),
    )
    return {"deleted": True}


@app.get("/imports/example")
def import_example(user: User = Depends(current_user)) -> Response:
    del user
    content = (
        "date,title,type,intensity,duration_minutes,workout_notes,exercise,category,set_count,reps,"
        "load_kg,duration_seconds,difficulty,assistance_kg,set_notes\n"
        "2026-08-19,Push technique,Push,7,60,Séance contrôlée,Tuck planche,figure,3,0,0,20,7,0,Bon contrôle\n"
    )
    return Response(
        content="\ufeff" + content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="skilltrack-exemple.csv"'},
    )


@app.get("/exports/json")
def export_json(
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> JSONResponse:
    payload = build_json_export(repository, user, API_VERSION)
    return JSONResponse(
        content=jsonable_encoder(payload),
        headers={"Content-Disposition": 'attachment; filename="skilltrack-export.json"'},
    )


@app.get("/exports/csv")
def export_csv(
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> Response:
    return Response(
        content=build_csv_export(repository, user),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="skilltrack-export.csv"'},
    )


@app.delete("/users/me")
def delete_me(
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
    user: User = Depends(current_user),
) -> dict:
    deletion_scope = repository.owned_counts(user.id)
    owner_ref = pseudonymous_reference(user.id)
    repository.delete(user)
    repository.commit()
    log_event(logger, logging.INFO, "user_data_deletion", status="completed", owner_ref=owner_ref, **deletion_scope)
    return {"deleted": True, "scope": deletion_scope}
