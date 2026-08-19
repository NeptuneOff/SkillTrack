from datetime import date, timedelta
import csv, io, json
from typing import Any
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text as sql_text
from sqlalchemy.orm import Session, joinedload
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.db import Base, engine, get_db, SessionLocal
from app.models import User, Workout, TrainingSet, Goal, ImportJob
from app.schemas import LoginIn, Token, UserOut, WorkoutIn, WorkoutOut, GoalIn, GoalOut, DashboardOut
from app.deps import current_user
from app.services import create_workout, update_workout, make_workout_out, dashboard

app = FastAPI(title="SkillTrack API", version="1.0.0")
origins = [o.strip() for o in settings.backend_cors_origins.split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    migrate_demo_schema()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == settings.demo_email).first()
        if not user:
            user = User(email=settings.demo_email, display_name="Demo", password_hash=hash_password(settings.demo_password))
            db.add(user); db.commit(); db.refresh(user)
        if db.query(Workout).filter(Workout.owner_id == user.id).count() < 3:
            seed_demo_data(db, user)
    finally:
        db.close()

def migrate_demo_schema():
    """Small, idempotent compatibility migration for pre-existing demo volumes.

    A production deployment should replace this with Alembic; keeping it here makes
    the jury's existing Docker volume upgrade without manual intervention.
    """
    additions = {
        "workouts": {"owner_id": "VARCHAR(36)", "date": "DATE", "type": "VARCHAR(80) DEFAULT 'Technique'", "intensity": "INTEGER DEFAULT 6", "duration_minutes": "INTEGER DEFAULT 60"},
        "training_sets": {"category": "VARCHAR(40) DEFAULT 'autre'", "set_count": "INTEGER DEFAULT 1", "assistance_kg": "FLOAT DEFAULT 0"},
        "goals": {"goal_type": "VARCHAR(40) DEFAULT 'figure'", "current_value": "FLOAT DEFAULT 0", "target_value": "FLOAT DEFAULT 1", "unit": "VARCHAR(40) DEFAULT 'autre'", "priority": "VARCHAR(20) DEFAULT 'moyenne'", "notes": "TEXT DEFAULT ''", "status": "VARCHAR(20) DEFAULT 'actif'"},
        "import_jobs": {"owner_id": "VARCHAR(36)", "filename": "VARCHAR(255) DEFAULT 'legacy-import.csv'", "imported_rows": "INTEGER DEFAULT 0", "rejected_rows": "INTEGER DEFAULT 0", "report": "TEXT DEFAULT ''"},
    }
    with engine.begin() as connection:
        known = inspect(connection)
        for table, columns in additions.items():
            existing = {column["name"] for column in known.get_columns(table)}
            for name, definition in columns.items():
                if name not in existing:
                    connection.execute(sql_text(f"ALTER TABLE {table} ADD COLUMN {name} {definition}"))
        # Preserve data created by the previous modular version of SkillTrack.
        workout_columns = {column["name"] for column in inspect(connection).get_columns("workouts")}
        if {"user_id", "owner_id"} <= workout_columns:
            connection.execute(sql_text("UPDATE workouts SET owner_id = user_id WHERE owner_id IS NULL"))
        if {"performed_on", "date"} <= workout_columns:
            connection.execute(sql_text("UPDATE workouts SET date = performed_on WHERE date IS NULL"))
        import_columns = {column["name"] for column in inspect(connection).get_columns("import_jobs")}
        if {"user_id", "owner_id"} <= import_columns:
            connection.execute(sql_text("UPDATE import_jobs SET owner_id = user_id WHERE owner_id IS NULL"))
        if {"file_name", "filename"} <= import_columns:
            connection.execute(sql_text("UPDATE import_jobs SET filename = file_name WHERE filename IS NULL OR filename = 'legacy-import.csv'"))
        if {"rows_accepted", "imported_rows"} <= import_columns:
            connection.execute(sql_text("UPDATE import_jobs SET imported_rows = rows_accepted WHERE imported_rows = 0"))
        if {"rows_rejected", "rejected_rows"} <= import_columns:
            connection.execute(sql_text("UPDATE import_jobs SET rejected_rows = rows_rejected WHERE rejected_rows = 0"))
        if {"error_report", "report"} <= import_columns:
            connection.execute(sql_text("UPDATE import_jobs SET report = error_report WHERE report = ''"))
        if engine.dialect.name == "postgresql":
            # Legacy-only required columns are no longer written by the current ORM.
            for table, columns in {
                "workouts": ("user_id", "performed_on"),
                "import_jobs": ("user_id", "file_name", "file_hash", "status", "rows_read", "rows_accepted", "rows_rejected"),
            }.items():
                present = {column["name"] for column in inspect(connection).get_columns(table)}
                for column in columns:
                    if column in present:
                        connection.execute(sql_text(f"ALTER TABLE {table} ALTER COLUMN {column} DROP NOT NULL"))

def seed_demo_data(db: Session, user: User):
    base = date.today()
    examples = [
        ("Planche technique", "Planche", 7, [("Tuck planche hold", 0, 0, 20, 7), ("Pseudo planche push-up", 8, 0, 0, 8)]),
        ("Front lever contrôle", "Pull", 6, [("Advanced tuck front lever", 0, 0, 25, 6), ("Tractions tempo", 6, 10, 0, 7)]),
        ("Force poussée", "Push", 8, [("Dips lestés", 5, 40, 0, 8), ("Handstand push-up", 4, 0, 0, 7)]),
    ]
    for i, (title, typ, intensity, sets) in enumerate(examples):
        w = Workout(owner_id=user.id, title=title, date=base - timedelta(days=i*3), type=typ, intensity=intensity, duration_minutes=75, notes="Données de démonstration")
        for ex, reps, load, dur, diff in sets:
            w.sets.append(TrainingSet(exercise=ex, category="autre", set_count=1, reps=reps, load_kg=load, duration_seconds=dur, difficulty=diff, assistance_kg=0, notes=""))
        db.add(w)
    db.add_all([
        Goal(owner_id=user.id, skill="Full planche", target="Tenir 5 secondes propre", current_level="Straddle / full courte", deadline=base + timedelta(days=90)),
        Goal(owner_id=user.id, skill="Front lever", target="20 secondes propres", current_level="Avancé", deadline=base + timedelta(days=60)),
        Goal(owner_id=user.id, skill="HSPU", target="10 répétitions strictes", current_level="6-8 reps", deadline=base + timedelta(days=45)),
        Goal(owner_id=user.id, skill="Handstand", target="Tenir 30 secondes", current_level="30 secondes", current_value=30, target_value=30, unit="secondes", status="termine", is_done=True),
    ])
    db.commit()

@app.get("/health")
def health(): return {"status": "ok", "app": "SkillTrack"}

@app.post("/auth/login", response_model=Token)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return Token(access_token=create_access_token(user.id))

@app.get("/users/me", response_model=UserOut)
def me(user: User = Depends(current_user)): return user

@app.get("/dashboard", response_model=DashboardOut)
def get_dashboard(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return dashboard(db, user)

@app.get("/workouts", response_model=list[WorkoutOut])
def list_workouts(db: Session = Depends(get_db), user: User = Depends(current_user)):
    workouts = db.query(Workout).options(joinedload(Workout.sets)).filter(Workout.owner_id == user.id).order_by(Workout.date.desc()).all()
    return [make_workout_out(w) for w in workouts]

@app.post("/workouts", response_model=WorkoutOut)
def post_workout(data: WorkoutIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return make_workout_out(create_workout(db, user, data))

@app.get("/workouts/{workout_id}", response_model=WorkoutOut)
def get_workout(workout_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    w = db.query(Workout).options(joinedload(Workout.sets)).filter(Workout.id == workout_id, Workout.owner_id == user.id).first()
    if not w: raise HTTPException(404, "Workout not found")
    return make_workout_out(w)

@app.put("/workouts/{workout_id}", response_model=WorkoutOut)
def put_workout(workout_id: str, data: WorkoutIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    w = db.query(Workout).options(joinedload(Workout.sets)).filter(Workout.id == workout_id, Workout.owner_id == user.id).first()
    if not w: raise HTTPException(404, "Workout not found")
    return make_workout_out(update_workout(db, w, data))

@app.delete("/workouts/{workout_id}")
def delete_workout(workout_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    w = db.query(Workout).filter(Workout.id == workout_id, Workout.owner_id == user.id).first()
    if not w: raise HTTPException(404, "Workout not found")
    db.delete(w); db.commit(); return {"deleted": True}

@app.get("/goals", response_model=list[GoalOut])
def list_goals(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.query(Goal).filter(Goal.owner_id == user.id).order_by(Goal.is_done.asc()).all()

@app.post("/goals", response_model=GoalOut)
def add_goal(data: GoalIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    g = Goal(owner_id=user.id, **data.model_dump()); db.add(g); db.commit(); db.refresh(g); return g

@app.put("/goals/{goal_id}", response_model=GoalOut)
def edit_goal(goal_id: str, data: GoalIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    g = db.query(Goal).filter(Goal.id == goal_id, Goal.owner_id == user.id).first()
    if not g: raise HTTPException(404, "Goal not found")
    for k,v in data.model_dump().items(): setattr(g,k,v)
    db.commit(); db.refresh(g); return g

@app.delete("/goals/{goal_id}")
def remove_goal(goal_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    g = db.query(Goal).filter(Goal.id == goal_id, Goal.owner_id == user.id).first()
    if not g: raise HTTPException(404, "Goal not found")
    db.delete(g); db.commit(); return {"deleted": True}

@app.post("/imports/csv")
def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(415, "Le fichier doit être au format CSV.")
    raw = file.file.read(2_000_001)
    if len(raw) > 2_000_000:
        raise HTTPException(413, "Le fichier CSV dépasse la limite de 2 Mo.")
    try:
        decoded = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(422, "Le fichier doit être encodé en UTF-8.") from exc
    reader = csv.DictReader(io.StringIO(decoded))
    required = {"date", "title", "exercise"}
    missing = required - set(reader.fieldnames or [])
    if missing:
        raise HTTPException(422, f"Colonnes obligatoires manquantes : {', '.join(sorted(missing))}")
    imported, rejected, errors = 0, 0, []
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for line_no, row in enumerate(reader, start=2):
        try:
            d = date.fromisoformat(row["date"])
            key = (d.isoformat(), row["title"])
            grouped.setdefault(key, {"title": row["title"], "date": d, "type": row.get("type") or "Import", "intensity": int(row.get("intensity") or 6), "duration_minutes": int(row.get("duration_minutes") or 60), "notes": "Import CSV", "sets": []})
            grouped[key]["sets"].append({"exercise": row["exercise"], "reps": int(row.get("reps") or 0), "load_kg": float(row.get("load_kg") or 0), "duration_seconds": int(row.get("duration_seconds") or 0), "difficulty": int(row.get("difficulty") or 5), "notes": row.get("notes") or ""})
            imported += 1
        except Exception as exc:
            rejected += 1; errors.append(f"Ligne {line_no}: {exc}")
    for item in grouped.values(): create_workout(db, user, WorkoutIn(**item))
    job = ImportJob(owner_id=user.id, filename=file.filename or "import.csv", imported_rows=imported, rejected_rows=rejected, report="\n".join(errors))
    db.add(job); db.commit()
    return {"imported_rows": imported, "rejected_rows": rejected, "errors": errors}

@app.get("/imports/history")
def import_history(db: Session = Depends(get_db), user: User = Depends(current_user)):
    jobs = db.query(ImportJob).filter(ImportJob.owner_id == user.id).order_by(ImportJob.created_at.desc()).limit(20).all()
    return [{"id": job.id, "filename": job.filename, "imported_rows": job.imported_rows, "rejected_rows": job.rejected_rows, "errors": job.report.splitlines() if job.report else [], "created_at": job.created_at} for job in jobs]

@app.get("/imports/example")
def import_example(user: User = Depends(current_user)):
    content = "date,title,type,intensity,duration_minutes,exercise,reps,load_kg,duration_seconds,difficulty,notes\n2026-08-19,Push technique,Push,7,60,Tuck planche,0,0,20,7,Bon contrôle\n"
    return Response(content=content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=skilltrack-exemple.csv"})

@app.get("/exports/json")
def export_json(db: Session = Depends(get_db), user: User = Depends(current_user)):
    data = dashboard(db, user)
    return Response(content=json.dumps(data, default=str, ensure_ascii=False, indent=2), media_type="application/json", headers={"Content-Disposition":"attachment; filename=skilltrack-export.json"})

@app.get("/exports/csv")
def export_csv(db: Session = Depends(get_db), user: User = Depends(current_user)):
    workouts = db.query(Workout).options(joinedload(Workout.sets)).filter(Workout.owner_id == user.id).all()
    out = io.StringIO(); writer = csv.writer(out)
    writer.writerow(["date","title","type","intensity","duration_minutes","exercise","reps","load_kg","duration_seconds","difficulty","notes"])
    for w in workouts:
        for s in w.sets:
            writer.writerow([w.date, w.title, w.type, w.intensity, w.duration_minutes, s.exercise, s.reps, s.load_kg, s.duration_seconds, s.difficulty, s.notes])
    return Response(content=out.getvalue(), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=skilltrack-export.csv"})

@app.delete("/users/me")
def delete_me(db: Session = Depends(get_db), user: User = Depends(current_user)):
    db.delete(user); db.commit(); return {"deleted": True}
