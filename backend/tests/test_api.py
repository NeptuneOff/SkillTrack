from __future__ import annotations

import csv
import io
from datetime import date
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session as OrmSession

from app.core.security import hash_password
from app.db import SessionLocal, engine
from app.main import (
    API_CONTENT_SECURITY_POLICY,
    DOCUMENTATION_CONTENT_SECURITY_POLICY,
    app,
    initialise_database,
)
from app.models import Goal, ImportJob, TrainingSet, User, Workout
from app.services import dashboard as build_dashboard

PASSWORD = "TestPassword123!"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def account_factory():
    created_ids: list[str] = []

    def create_account(display_name: str = "Test utilisateur") -> dict[str, str]:
        email = f"pytest-{uuid4()}@skilltrack.dev"
        db = SessionLocal()
        try:
            user = User(email=email, display_name=display_name, password_hash=hash_password(PASSWORD))
            db.add(user)
            db.commit()
            db.refresh(user)
            created_ids.append(user.id)
            return {"id": user.id, "email": email, "password": PASSWORD, "display_name": display_name}
        finally:
            db.close()

    yield create_account

    db = SessionLocal()
    try:
        for user_id in created_ids:
            user = db.get(User, user_id)
            if user:
                db.delete(user)
        db.commit()
    finally:
        db.close()


def auth_headers(client: TestClient, account: dict[str, str]) -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": account["email"], "password": account["password"]},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def workout_payload(title: str = "Séance pytest", *, training_sets: list[dict] | None = None) -> dict:
    if training_sets is None:
        training_sets = [
            {
                "exercise": "Pull-up",
                "category": "tirage",
                "set_count": 3,
                "reps": 8,
                "load_kg": 12.5,
                "duration_seconds": 0,
                "difficulty": 7,
                "assistance_kg": 0,
                "notes": "Propre",
            }
        ]
    return {
        "title": title,
        "date": date.today().isoformat(),
        "type": "Force",
        "intensity": 7,
        "duration_minutes": 45,
        "notes": "Notes de séance",
        "sets": training_sets,
    }


def goal_payload(skill: str = "Full planche") -> dict:
    return {
        "skill": skill,
        "goal_type": "figure",
        "target": "Tenir 5 secondes",
        "current_level": "Straddle",
        "current_value": 2,
        "target_value": 5,
        "unit": "secondes",
        "priority": "haute",
        "notes": "Objectif pytest",
        "status": "actif",
        "deadline": None,
        "is_done": False,
    }


def test_health_and_security_headers(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "SkillTrack"}
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["content-security-policy"] == API_CONTENT_SECURITY_POLICY
    UUID(response.headers["x-request-id"])


def test_documentation_pages_have_a_scoped_csp_without_network_requests(client: TestClient):
    api_csp = client.get("/openapi.json").headers["content-security-policy"]
    assert api_csp == API_CONTENT_SECURITY_POLICY

    expected_pages = {
        "/docs": ("Swagger UI", "https://cdn.jsdelivr.net", "https://fastapi.tiangolo.com"),
        "/redoc": ("ReDoc", "https://cdn.jsdelivr.net", "https://fonts.googleapis.com"),
    }
    for path, expected_content in expected_pages.items():
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert "/openapi.json" in response.text
        assert all(value in response.text for value in expected_content)

        assert response.headers["content-security-policy"] == DOCUMENTATION_CONTENT_SECURITY_POLICY


def test_authentication_and_protected_routes(client: TestClient, account_factory):
    account = account_factory()
    bad_login = client.post("/auth/login", json={"email": account["email"], "password": "WrongPassword!"})
    assert bad_login.status_code == 401
    oversized_password = client.post(
        "/auth/login",
        json={"email": account["email"], "password": "é" * 40},
    )
    assert oversized_password.status_code == 422
    for path in ("/users/me", "/dashboard", "/workouts", "/goals", "/exports/json", "/exports/csv"):
        assert client.get(path).status_code in (401, 403)
    headers = auth_headers(client, account)
    profile = client.get("/users/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["email"] == account["email"]
    assert "password_hash" not in profile.json()


def test_workout_create_update_remove_sets_and_delete(client: TestClient, account_factory):
    account = account_factory()
    headers = auth_headers(client, account)
    created = client.post("/workouts", json=workout_payload(), headers=headers)
    assert created.status_code == 200, created.text
    workout_id = created.json()["id"]
    old_set_id = created.json()["sets"][0]["id"]

    updated_payload = workout_payload(
        "Séance modifiée",
        training_sets=[
            {
                "exercise": "Dips",
                "category": "poussée",
                "set_count": 4,
                "reps": 6,
                "load_kg": 20,
                "duration_seconds": 0,
                "difficulty": 8,
                "assistance_kg": 0,
                "notes": "Nouvelle série",
            }
        ],
    )
    updated = client.put(f"/workouts/{workout_id}", json=updated_payload, headers=headers)
    assert updated.status_code == 200, updated.text
    assert updated.json()["title"] == "Séance modifiée"
    assert updated.json()["sets"][0]["exercise"] == "Dips"
    assert updated.json()["sets"][0]["id"] != old_set_id
    with SessionLocal() as db:
        assert db.get(TrainingSet, old_set_id) is None

    no_exercise = {**updated_payload, "sets": []}
    emptied = client.put(f"/workouts/{workout_id}", json=no_exercise, headers=headers)
    assert emptied.status_code == 200
    assert emptied.json()["sets"] == []
    invalid = {**updated_payload, "intensity": 11}
    assert client.post("/workouts", json=invalid, headers=headers).status_code == 422
    assert client.delete(f"/workouts/{workout_id}", headers=headers).status_code == 200
    assert client.get(f"/workouts/{workout_id}", headers=headers).status_code == 404


def test_dashboard_uses_real_set_count_and_volume(client: TestClient, account_factory):
    account = account_factory()
    headers = auth_headers(client, account)
    payload = workout_payload(
        "Agrégats",
        training_sets=[
            {
                "exercise": "Dips",
                "category": "poussée",
                "set_count": 3,
                "reps": 10,
                "load_kg": 20,
                "duration_seconds": 0,
                "difficulty": 7,
                "assistance_kg": 5,
                "notes": "",
            },
            {
                "exercise": "Planche hold",
                "category": "figure",
                "set_count": 2,
                "reps": 0,
                "load_kg": 0,
                "duration_seconds": 30,
                "difficulty": 8,
                "assistance_kg": 0,
                "notes": "",
            },
        ],
    )
    assert client.post("/workouts", json=payload, headers=headers).status_code == 200
    active_goal = client.post("/goals", json=goal_payload("Objectif actif"), headers=headers)
    completed_goal = client.post(
        "/goals",
        json={**goal_payload("Objectif terminé"), "status": "termine", "is_done": True},
        headers=headers,
    )
    assert active_goal.status_code == 200
    assert completed_goal.status_code == 200
    dashboard = client.get("/dashboard", headers=headers)
    assert dashboard.status_code == 200
    data = dashboard.json()
    assert data["workout_count"] == 1
    assert data["set_count"] == 5
    assert data["exercise_count"] == 2
    assert data["total_volume"] == 462.0
    assert data["total_duration_minutes"] == 45
    assert data["average_intensity"] == 7.0
    assert data["last_workout"]["title"] == "Agrégats"
    assert [goal["skill"] for goal in data["goals"]] == ["Objectif actif"]


def test_dashboard_business_logic_accepts_a_substituted_storage_port():
    owner = User(
        id=str(uuid4()),
        email="storage-port@skilltrack.dev",
        display_name="Storage port",
        password_hash="not-used",
    )
    workout = Workout(
        id=str(uuid4()),
        owner_id=owner.id,
        title="Repository indépendant",
        date=date.today(),
        type="Force",
        intensity=8,
        duration_minutes=30,
        notes="",
    )
    workout.sets.append(
        TrainingSet(
            id=str(uuid4()),
            exercise="Dips",
            category="poussée",
            set_count=4,
            reps=5,
            load_kg=10,
            duration_seconds=0,
            difficulty=7,
            assistance_kg=0,
            notes="",
        )
    )
    goal = Goal(
        id=str(uuid4()),
        owner_id=owner.id,
        skill="Planche",
        target="Tenir 5 secondes",
        current_level="Tuck",
        status="actif",
        is_done=False,
    )
    repository = MagicMock()
    repository.workouts_for_owner.return_value = [workout]
    repository.goals_for_owner.return_value = [goal]

    result = build_dashboard(repository, owner)

    repository.workouts_for_owner.assert_called_once_with(owner.id)
    repository.goals_for_owner.assert_called_once_with(owner.id, active_only=True)
    assert result["workout_count"] == 1
    assert result["set_count"] == 4
    assert result["goals"] == [goal]


def test_restart_does_not_resurrect_deleted_demo_records(account_factory, monkeypatch):
    account = account_factory("Compte démo existant vide")
    monkeypatch.setattr("app.main.settings.demo_email", account["email"])
    monkeypatch.setattr("app.main.run_migrations", lambda: None)

    initialise_database()

    with SessionLocal() as db:
        assert db.query(Workout).filter(Workout.owner_id == account["id"]).count() == 0
        assert db.query(Goal).filter(Goal.owner_id == account["id"]).count() == 0


def test_goal_completion_triggers_mailhog_once_without_logging_personal_data(
    client: TestClient,
    account_factory,
    monkeypatch,
    caplog,
):
    account = account_factory("Alice Test")
    headers = auth_headers(client, account)
    created = client.post("/goals", json=goal_payload("Muscle-up"), headers=headers)
    assert created.status_code == 200

    smtp = MagicMock()
    smtp.__enter__.return_value = smtp
    monkeypatch.setattr("app.notifications.smtplib.SMTP", MagicMock(return_value=smtp))
    # Le statut est canonique : le validateur Pydantic aligne is_done même si un
    # ancien client envoie encore une valeur incohérente.
    completed_payload = {**goal_payload("Muscle-up"), "status": "termine", "is_done": False, "current_value": 5}
    with caplog.at_level("INFO"):
        completed = client.put(f"/goals/{created.json()['id']}", json=completed_payload, headers=headers)
    assert completed.status_code == 200
    assert completed.json()["is_done"] is True
    smtp.send_message.assert_called_once()
    sent_message = smtp.send_message.call_args.args[0]
    assert sent_message["To"] == account["email"]
    assert "Muscle-up" in sent_message.get_content()
    assert account["email"] not in caplog.text
    assert "Muscle-up" not in caplog.text

    repeated = client.put(f"/goals/{created.json()['id']}", json=completed_payload, headers=headers)
    assert repeated.status_code == 200
    smtp.send_message.assert_called_once()

    unavailable = client.post("/goals", json=goal_payload("SMTP indisponible"), headers=headers).json()
    monkeypatch.setattr("app.notifications.smtplib.SMTP", MagicMock(side_effect=OSError("offline")))
    unavailable_payload = {
        **goal_payload("SMTP indisponible"),
        "status": "termine",
        "is_done": True,
        "current_value": 5,
    }
    still_completed = client.put(
        f"/goals/{unavailable['id']}",
        json=unavailable_payload,
        headers=headers,
    )
    assert still_completed.status_code == 200
    assert still_completed.json()["is_done"] is True


def test_csv_import_validates_each_row_and_keeps_a_report(client: TestClient, account_factory):
    account = account_factory()
    headers = auth_headers(client, account)
    csv_data = (
        "date;title;type;intensity;duration_minutes;workout_notes;exercise;category;set_count;reps;"
        "load_kg;duration_seconds;difficulty;assistance_kg;set_notes\n"
        f"{date.today().isoformat()};Import robuste;Force;8;50;Séance importée;Pull-up;tirage;4;5;15;0;7;2;Valide\n"
        "date-invalide;Rejet date;Force;8;50;;Dips;poussée;3;8;0;0;7;0;Erreur\n"
        f"{date.today().isoformat()};Rejet difficulté;Force;8;50;;Dips;poussée;3;8;0;0;99;0;Erreur\n"
    )
    response = client.post(
        "/imports/csv",
        files={"file": ("dossier/prive/workouts.csv", csv_data.encode(), "text/csv")},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    report = response.json()
    assert report["status"] == "completed_with_errors"
    assert report["imported_rows"] == 1
    assert report["rejected_rows"] == 2
    assert report["created_workouts"] == 1
    assert all("Ligne" in error for error in report["errors"])

    workouts = client.get("/workouts", headers=headers).json()
    imported = next(workout for workout in workouts if workout["title"] == "Import robuste")
    assert imported["notes"] == "Séance importée"
    assert imported["sets"][0] == {
        **imported["sets"][0],
        "exercise": "Pull-up",
        "category": "tirage",
        "set_count": 4,
        "reps": 5,
        "load_kg": 15.0,
        "duration_seconds": 0,
        "difficulty": 7,
        "assistance_kg": 2.0,
        "notes": "Valide",
    }
    history = client.get("/imports/history", headers=headers).json()
    assert history[0]["filename"] == "workouts.csv"
    assert history[0]["rejected_rows"] == 2
    assert len(history[0]["errors"]) == 2


def test_csv_import_rejects_type_beyond_database_limit_without_partial_insert(
    client: TestClient,
    account_factory,
):
    account = account_factory()
    headers = auth_headers(client, account)
    title = f"Type trop long {uuid4()}"
    csv_data = (
        "date,title,type,exercise,reps\n"
        f"{date.today().isoformat()},{title},{'x' * 81},Dips,8\n"
    )

    response = client.post(
        "/imports/csv",
        files={"file": ("type-trop-long.csv", csv_data, "text/csv")},
        headers=headers,
    )

    assert response.status_code == 200, response.text
    report = response.json()
    assert report["status"] == "rejected"
    assert report["imported_rows"] == 0
    assert report["rejected_rows"] == 1
    assert report["created_workouts"] == 0
    assert len(report["errors"]) == 1
    assert "Ligne 2" in report["errors"][0]
    assert "valeurs sont invalides" in report["errors"][0]

    with SessionLocal() as db:
        assert db.query(Workout).filter(Workout.owner_id == account["id"], Workout.title == title).count() == 0
        job = db.get(ImportJob, report["import_id"])
        assert job is not None
        assert job.rejected_rows == 1
        assert job.imported_rows == 0
        assert job.report == report["errors"][0]


@pytest.mark.parametrize(
    ("filename", "content", "expected_status", "detail"),
    [
        ("workouts.txt", b"date,title,exercise\n", 415, "format CSV"),
        ("workouts.csv", b"\xff\xfe", 422, "UTF-8"),
        ("workouts.csv", b"foo,bar\n1,2\n", 422, "Colonnes obligatoires"),
        ("workouts.csv", b"date,date,title,exercise\n2026-01-01,2026-01-01,A,Dips\n", 422, "double"),
    ],
)
def test_csv_import_rejects_invalid_files(
    client: TestClient,
    account_factory,
    filename: str,
    content: bytes,
    expected_status: int,
    detail: str,
):
    headers = auth_headers(client, account_factory())
    response = client.post("/imports/csv", files={"file": (filename, content, "text/csv")}, headers=headers)
    assert response.status_code == expected_status
    assert detail in response.json()["detail"]


def test_csv_import_rolls_back_everything_on_database_error(client: TestClient, account_factory, monkeypatch):
    account = account_factory()
    headers = auth_headers(client, account)
    title = f"Rollback {uuid4()}"
    csv_data = f"date,title,exercise,reps\n{date.today().isoformat()},{title},Dips,8\n"
    original_commit = OrmSession.commit

    def failing_commit(session: OrmSession):
        if any(isinstance(item, ImportJob) for item in session.new):
            raise SQLAlchemyError("forced import failure")
        return original_commit(session)

    monkeypatch.setattr(OrmSession, "commit", failing_commit)
    response = client.post(
        "/imports/csv",
        files={"file": ("rollback.csv", csv_data, "text/csv")},
        headers=headers,
    )
    assert response.status_code == 500
    assert "aucune donnée" in response.json()["detail"]
    with SessionLocal() as db:
        assert db.query(Workout).filter(Workout.owner_id == account["id"], Workout.title == title).count() == 0
        assert db.query(ImportJob).filter(ImportJob.owner_id == account["id"]).count() == 0


def test_multi_user_isolation_on_every_owned_resource(client: TestClient, account_factory):
    owner = account_factory("Propriétaire")
    stranger = account_factory("Autre utilisateur")
    owner_headers = auth_headers(client, owner)
    stranger_headers = auth_headers(client, stranger)
    workout = client.post("/workouts", json=workout_payload("Privée"), headers=owner_headers).json()
    goal = client.post("/goals", json=goal_payload("Objectif privé"), headers=owner_headers).json()
    csv_data = f"date,title,exercise\n{date.today().isoformat()},Import privé,Dips\n"
    import_response = client.post(
        "/imports/csv",
        files={"file": ("private.csv", csv_data, "text/csv")},
        headers=owner_headers,
    )
    assert import_response.status_code == 200
    assert import_response.json()["import_id"] == import_response.json()["id"]

    assert client.get("/workouts", headers=stranger_headers).json() == []
    assert client.get(f"/workouts/{workout['id']}", headers=stranger_headers).status_code == 404
    assert client.put(
        f"/workouts/{workout['id']}", json=workout_payload("Volée"), headers=stranger_headers
    ).status_code == 404
    assert client.delete(f"/workouts/{workout['id']}", headers=stranger_headers).status_code == 404
    assert client.get("/goals", headers=stranger_headers).json() == []
    assert client.put(f"/goals/{goal['id']}", json=goal_payload(), headers=stranger_headers).status_code == 404
    assert client.delete(f"/goals/{goal['id']}", headers=stranger_headers).status_code == 404
    assert client.get("/imports/history", headers=stranger_headers).json() == []
    import_id = import_response.json()["import_id"]
    assert client.delete(f"/imports/history/{import_id}", headers=stranger_headers).status_code == 404
    stranger_export = client.get("/exports/json", headers=stranger_headers).json()
    assert stranger_export["profile"]["id"] == stranger["id"]
    assert stranger_export["workouts"] == []
    assert stranger_export["goals"] == []
    assert stranger_export["imports"] == []
    assert client.delete(f"/imports/history/{import_id}", headers=owner_headers).status_code == 200
    assert client.get("/imports/history", headers=owner_headers).json() == []


def test_json_export_is_complete_and_serialises_nested_data(client: TestClient, account_factory):
    account = account_factory()
    headers = auth_headers(client, account)
    for index in range(6):
        assert client.post("/workouts", json=workout_payload(f"Séance export {index}"), headers=headers).status_code == 200
    assert client.post("/goals", json=goal_payload("Objectif export"), headers=headers).status_code == 200
    csv_data = f"date,title,exercise\n{date.today().isoformat()},Import export,Rows\n"
    assert client.post(
        "/imports/csv", files={"file": ("export.csv", csv_data, "text/csv")}, headers=headers
    ).status_code == 200

    response = client.get("/exports/json", headers=headers)
    assert response.status_code == 200
    assert "attachment" in response.headers["content-disposition"]
    data = response.json()
    assert data["metadata"]["format"] == "skilltrack-data-export"
    assert data["metadata"]["schema_version"] == "1.0"
    assert data["metadata"]["scope"] == "all_user_data"
    assert data["profile"]["email"] == account["email"]
    assert "password_hash" not in data["profile"]
    assert len(data["workouts"]) == 7
    assert data["metadata"]["counts"] == {
        "workouts": 7,
        "training_sets": 7,
        "goals": 1,
        "imports": 1,
    }
    assert isinstance(data["workouts"][0]["sets"][0], dict)
    assert "exercise" in data["workouts"][0]["sets"][0]
    assert data["goals"][0]["skill"] == "Objectif export"
    assert data["imports"][0]["filename"] == "export.csv"
    assert "object at" not in response.text


def test_complete_csv_export_round_trip_preserves_workouts_goals_and_audit_rows(
    client: TestClient,
    account_factory,
):
    source = account_factory("Source CSV")
    target = account_factory("Cible CSV")
    source_headers = auth_headers(client, source)
    target_headers = auth_headers(client, target)
    special_payload = workout_payload(
        "=2+2",
        training_sets=[
            {
                "exercise": "Dips, stricts",
                "category": "poussée",
                "set_count": 4,
                "reps": 6,
                "load_kg": 25.5,
                "duration_seconds": 0,
                "difficulty": 8,
                "assistance_kg": 1.5,
                "notes": "Ligne 1\nLigne 2",
            },
            {
                "exercise": "Planche hold",
                "category": "figure",
                "set_count": 2,
                "reps": 0,
                "load_kg": 0,
                "duration_seconds": 12,
                "difficulty": 9,
                "assistance_kg": 0,
                "notes": "@note tableur",
            },
        ],
    )
    special_payload["notes"] = "Séance, complète\nDeuxième ligne"
    assert client.post("/workouts", json=special_payload, headers=source_headers).status_code == 200
    assert client.post(
        "/workouts", json=workout_payload("Sans exercice", training_sets=[]), headers=source_headers
    ).status_code == 200
    assert client.post("/goals", json=goal_payload("Objectif CSV"), headers=source_headers).status_code == 200
    simple_import = f"date,title,exercise\n{date.today().isoformat()},Import historique,Dips\n"
    assert client.post(
        "/imports/csv",
        files={"file": ("historique.csv", simple_import, "text/csv")},
        headers=source_headers,
    ).status_code == 200

    exported = client.get("/exports/csv", headers=source_headers)
    assert exported.status_code == 200
    decoded = exported.content.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(decoded)))
    record_types = {row["record_type"] for row in rows}
    assert record_types == {"metadata", "profile", "workout", "training_set", "goal", "import"}
    assert any(row["record_type"] == "workout" and row["title"] == "'=2+2" for row in rows)
    assert any(row["record_type"] == "workout" and row["title"] == "Sans exercice" for row in rows)
    assert any(row["record_type"] == "import" and row["filename"] == "historique.csv" for row in rows)

    imported = client.post(
        "/imports/csv",
        files={"file": ("round-trip.csv", exported.content, "text/csv")},
        headers=target_headers,
    )
    assert imported.status_code == 200, imported.text
    report = imported.json()
    assert report["status"] == "completed"
    assert report["created_workouts"] == 3
    assert report["created_goals"] == 1
    assert report["ignored_rows"] == 3
    target_workouts = client.get("/workouts", headers=target_headers).json()
    special = next(workout for workout in target_workouts if workout["title"] == "=2+2")
    assert special["notes"] == special_payload["notes"]
    assert special["sets"][0]["set_count"] == 4
    assert special["sets"][0]["assistance_kg"] == 1.5
    assert special["sets"][0]["notes"] == "Ligne 1\nLigne 2"
    assert next(workout for workout in target_workouts if workout["title"] == "Sans exercice")["sets"] == []
    target_goals = client.get("/goals", headers=target_headers).json()
    assert [goal["skill"] for goal in target_goals] == ["Objectif CSV"]
    target_history = client.get("/imports/history", headers=target_headers).json()
    assert len(target_history) == 1
    assert target_history[0]["filename"] == "round-trip.csv"


def test_rgpd_deletion_cascades_to_all_owned_data(client: TestClient, account_factory):
    account = account_factory()
    headers = auth_headers(client, account)
    assert client.post("/workouts", json=workout_payload("À supprimer"), headers=headers).status_code == 200
    assert client.post("/goals", json=goal_payload("À supprimer"), headers=headers).status_code == 200
    csv_data = f"date,title,exercise\n{date.today().isoformat()},Import à supprimer,Dips\n"
    assert client.post(
        "/imports/csv", files={"file": ("delete.csv", csv_data, "text/csv")}, headers=headers
    ).status_code == 200
    with SessionLocal() as db:
        workout_ids = [row[0] for row in db.query(Workout.id).filter(Workout.owner_id == account["id"]).all()]
        assert workout_ids
        assert db.query(TrainingSet).filter(TrainingSet.workout_id.in_(workout_ids)).count() == 2

    deleted = client.delete("/users/me", headers=headers)
    assert deleted.status_code == 200, deleted.text
    assert deleted.json()["scope"] == {"workouts": 2, "training_sets": 2, "goals": 1, "imports": 1}
    assert client.get("/users/me", headers=headers).status_code == 401
    with SessionLocal() as db:
        assert db.get(User, account["id"]) is None
        assert db.query(Workout).filter(Workout.owner_id == account["id"]).count() == 0
        assert db.query(TrainingSet).filter(TrainingSet.workout_id.in_(workout_ids)).count() == 0
        assert db.query(Goal).filter(Goal.owner_id == account["id"]).count() == 0
        assert db.query(ImportJob).filter(ImportJob.owner_id == account["id"]).count() == 0


def test_postgresql_schema_has_migration_constraints_indexes_and_business_trigger(
    client: TestClient,
    account_factory,
):
    del client
    if engine.dialect.name != "postgresql":
        pytest.skip("Preuve d'intégration réservée à PostgreSQL")
    inspector = inspect(engine)
    with engine.connect() as connection:
        assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "20260819_03"
        assert connection.execute(
            text("SELECT 1 FROM pg_trigger WHERE tgname = 'trg_goals_completion_consistency' AND NOT tgisinternal")
        ).scalar_one() == 1
    for table_name in ("workouts", "goals", "import_jobs"):
        foreign_keys = inspector.get_foreign_keys(table_name)
        owner_fk = next(foreign_key for foreign_key in foreign_keys if foreign_key["constrained_columns"] == ["owner_id"])
        assert owner_fk["referred_table"] == "users"
        assert owner_fk["options"]["ondelete"] == "CASCADE"
    workout_indexes = {index["name"] for index in inspector.get_indexes("workouts")}
    assert {"ix_workouts_owner_id", "ix_workouts_owner_date"} <= workout_indexes
    import_checks = {constraint["name"] for constraint in inspector.get_check_constraints("import_jobs")}
    assert "ck_import_jobs_ignored_rows" in import_checks
    goal_checks = {constraint["name"] for constraint in inspector.get_check_constraints("goals")}
    assert "ck_goals_completion_consistency" in goal_checks

    account = account_factory()
    with SessionLocal() as db:
        inconsistent = Goal(
            owner_id=account["id"],
            skill="Trigger SQL",
            target="Prouver la cohérence",
            current_level="Test",
            current_value=0,
            target_value=1,
            status="termine",
            is_done=False,
        )
        db.add(inconsistent)
        db.commit()
        db.refresh(inconsistent)
        assert inconsistent.status == "termine"
        assert inconsistent.is_done is True
