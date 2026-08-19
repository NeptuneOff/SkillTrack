from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from pydantic import ValidationError

from app.models import Goal, ImportJob, User, Workout
from app.repositories import SkillTrackRepository
from app.schemas import GoalIn, SetIn, WorkoutIn
from app.services import workout_volume

EXPORT_FORMAT = "skilltrack-data-export"
EXPORT_SCHEMA_VERSION = "1.0"

CSV_FIELDS = [
    "format_version",
    "record_type",
    "exported_at",
    "application",
    "profile_id",
    "email",
    "display_name",
    "profile_created_at",
    "workout_id",
    "date",
    "title",
    "type",
    "intensity",
    "duration_minutes",
    "workout_notes",
    "workout_created_at",
    "set_id",
    "exercise",
    "category",
    "set_count",
    "reps",
    "load_kg",
    "duration_seconds",
    "difficulty",
    "assistance_kg",
    "set_notes",
    "goal_id",
    "skill",
    "goal_type",
    "target",
    "current_level",
    "current_value",
    "target_value",
    "unit",
    "priority",
    "goal_notes",
    "status",
    "deadline",
    "is_done",
    "import_id",
    "filename",
    "imported_rows",
    "rejected_rows",
    "ignored_rows",
    "import_errors",
    "import_created_at",
]

LEGACY_REQUIRED_FIELDS = {"date", "title", "exercise"}
SUPPORTED_RECORD_TYPES = {"metadata", "profile", "workout", "training_set", "goal", "import"}
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


@dataclass
class CsvImportPlan:
    workouts: list[WorkoutIn] = field(default_factory=list)
    goals: list[GoalIn] = field(default_factory=list)
    imported_rows: int = 0
    rejected_rows: int = 0
    ignored_rows: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class _WorkoutGroup:
    data: dict[str, Any]
    sets: list[SetIn] = field(default_factory=list)
    counted_workout_row: bool = False


def _iso(value: Any) -> str:
    return value.isoformat() if value is not None else ""


def _safe_csv_value(value: Any) -> Any:
    """Neutralise les formules lors d'une ouverture du CSV dans un tableur."""
    if not isinstance(value, str) or not value.startswith(FORMULA_PREFIXES):
        return value
    return f"'{value}"


def _restore_csv_value(value: str | None) -> str:
    if value is None:
        return ""
    if len(value) >= 2 and value[0] == "'" and value[1] in FORMULA_PREFIXES:
        return value[1:]
    return value


def _workout_dict(workout: Workout) -> dict[str, Any]:
    return {
        "id": workout.id,
        "title": workout.title,
        "date": workout.date,
        "type": workout.type,
        "intensity": workout.intensity,
        "duration_minutes": workout.duration_minutes,
        "notes": workout.notes,
        "created_at": workout.created_at,
        "volume": workout_volume(workout),
        "sets": [
            {
                "id": training_set.id,
                "exercise": training_set.exercise,
                "category": training_set.category,
                "set_count": training_set.set_count,
                "reps": training_set.reps,
                "load_kg": training_set.load_kg,
                "duration_seconds": training_set.duration_seconds,
                "difficulty": training_set.difficulty,
                "assistance_kg": training_set.assistance_kg,
                "notes": training_set.notes,
            }
            for training_set in workout.sets
        ],
    }


def _goal_dict(goal: Goal) -> dict[str, Any]:
    return {
        "id": goal.id,
        "skill": goal.skill,
        "goal_type": goal.goal_type,
        "target": goal.target,
        "current_level": goal.current_level,
        "current_value": goal.current_value,
        "target_value": goal.target_value,
        "unit": goal.unit,
        "priority": goal.priority,
        "notes": goal.notes,
        "status": goal.status,
        "deadline": goal.deadline,
        "is_done": goal.is_done,
    }


def _import_dict(job: ImportJob) -> dict[str, Any]:
    return {
        "id": job.id,
        "filename": job.filename,
        "imported_rows": job.imported_rows,
        "rejected_rows": job.rejected_rows,
        "ignored_rows": job.ignored_rows,
        "errors": job.report.splitlines() if job.report else [],
        "created_at": job.created_at,
    }


def build_json_export(repository: SkillTrackRepository, user: User, api_version: str) -> dict[str, Any]:
    workouts = repository.workouts_for_owner(user.id)
    goals = repository.goals_for_owner(user.id)
    imports = repository.imports_for_owner(user.id)
    return {
        "metadata": {
            "application": "SkillTrack",
            "format": EXPORT_FORMAT,
            "schema_version": EXPORT_SCHEMA_VERSION,
            "api_version": api_version,
            "exported_at": datetime.now(UTC),
            "scope": "all_user_data",
            "counts": {
                "workouts": len(workouts),
                "training_sets": sum(len(workout.sets) for workout in workouts),
                "goals": len(goals),
                "imports": len(imports),
            },
        },
        "profile": {
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "created_at": user.created_at,
        },
        "workouts": [_workout_dict(workout) for workout in workouts],
        "goals": [_goal_dict(goal) for goal in goals],
        "imports": [_import_dict(job) for job in imports],
    }


def _row(record_type: str, **values: Any) -> dict[str, Any]:
    row: dict[str, Any] = {field_name: "" for field_name in CSV_FIELDS}
    row.update(format_version=EXPORT_SCHEMA_VERSION, record_type=record_type)
    row.update(values)
    return {key: _safe_csv_value(value) for key, value in row.items()}


def build_csv_export(repository: SkillTrackRepository, user: User) -> str:
    payload = build_json_export(repository, user, api_version="1.0.0")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    metadata = payload["metadata"]
    writer.writerow(
        _row(
            "metadata",
            exported_at=_iso(metadata["exported_at"]),
            application=metadata["application"],
        )
    )
    profile = payload["profile"]
    writer.writerow(
        _row(
            "profile",
            profile_id=profile["id"],
            email=profile["email"],
            display_name=profile["display_name"],
            profile_created_at=_iso(profile["created_at"]),
        )
    )
    for workout in payload["workouts"]:
        workout_values = {
            "workout_id": workout["id"],
            "date": _iso(workout["date"]),
            "title": workout["title"],
            "type": workout["type"],
            "intensity": workout["intensity"],
            "duration_minutes": workout["duration_minutes"],
            "workout_notes": workout["notes"],
            "workout_created_at": _iso(workout["created_at"]),
        }
        writer.writerow(_row("workout", **workout_values))
        for training_set in workout["sets"]:
            writer.writerow(
                _row(
                    "training_set",
                    **workout_values,
                    set_id=training_set["id"],
                    exercise=training_set["exercise"],
                    category=training_set["category"],
                    set_count=training_set["set_count"],
                    reps=training_set["reps"],
                    load_kg=training_set["load_kg"],
                    duration_seconds=training_set["duration_seconds"],
                    difficulty=training_set["difficulty"],
                    assistance_kg=training_set["assistance_kg"],
                    set_notes=training_set["notes"],
                )
            )
    for goal in payload["goals"]:
        writer.writerow(
            _row(
                "goal",
                goal_id=goal["id"],
                skill=goal["skill"],
                goal_type=goal["goal_type"],
                target=goal["target"],
                current_level=goal["current_level"],
                current_value=goal["current_value"],
                target_value=goal["target_value"],
                unit=goal["unit"],
                priority=goal["priority"],
                goal_notes=goal["notes"],
                status=goal["status"],
                deadline=_iso(goal["deadline"]),
                is_done=str(goal["is_done"]).lower(),
            )
        )
    for job in payload["imports"]:
        writer.writerow(
            _row(
                "import",
                import_id=job["id"],
                filename=job["filename"],
                imported_rows=job["imported_rows"],
                rejected_rows=job["rejected_rows"],
                ignored_rows=job["ignored_rows"],
                import_errors="\n".join(job["errors"]),
                import_created_at=_iso(job["created_at"]),
            )
        )
    return "\ufeff" + output.getvalue()


def _blank_default(value: str | None, default: Any) -> Any:
    return default if value is None or value.strip() == "" else value.strip()


def _text(row: dict[str, str | None], key: str, *, strip: bool = False) -> str:
    value = _restore_csv_value(row.get(key))
    return value.strip() if strip else value


def _workout_data(row: dict[str, str | None]) -> dict[str, Any]:
    return {
        "title": _text(row, "title", strip=True),
        "date": _text(row, "date", strip=True),
        "type": _blank_default(row.get("type"), "Import"),
        "intensity": _blank_default(row.get("intensity"), 6),
        "duration_minutes": _blank_default(row.get("duration_minutes"), 60),
        "notes": _text(row, "workout_notes") or "Import CSV",
    }


def _set_data(row: dict[str, str | None], *, legacy: bool) -> SetIn:
    notes_key = "notes" if legacy and "set_notes" not in row else "set_notes"
    return SetIn(
        exercise=_text(row, "exercise", strip=True),
        category=_blank_default(row.get("category"), "autre"),
        set_count=_blank_default(row.get("set_count"), 1),
        reps=_blank_default(row.get("reps"), 0),
        load_kg=_blank_default(row.get("load_kg"), 0),
        duration_seconds=_blank_default(row.get("duration_seconds"), 0),
        difficulty=_blank_default(row.get("difficulty"), 5),
        assistance_kg=_blank_default(row.get("assistance_kg"), 0),
        notes=_text(row, notes_key),
    )


def _goal_data(row: dict[str, str | None]) -> GoalIn:
    deadline = _text(row, "deadline", strip=True)
    return GoalIn.model_validate(
        {
            "skill": _text(row, "skill", strip=True),
            "goal_type": _blank_default(row.get("goal_type"), "figure"),
            "target": _text(row, "target", strip=True),
            "current_level": _blank_default(row.get("current_level"), "Début"),
            "current_value": _blank_default(row.get("current_value"), 0),
            "target_value": _blank_default(row.get("target_value"), 1),
            "unit": _blank_default(row.get("unit"), "autre"),
            "priority": _blank_default(row.get("priority"), "moyenne"),
            "notes": _text(row, "goal_notes"),
            "status": _blank_default(row.get("status"), "actif"),
            "deadline": deadline or None,
            "is_done": _blank_default(row.get("is_done"), False),
        }
    )


def _validation_message(line_no: int, _: ValidationError) -> str:
    # Never expose exception text to the client: validator messages may contain
    # implementation details. The line number remains actionable in the report.
    return f"Ligne {line_no} : une ou plusieurs valeurs sont invalides."


def _metadata_matches(left: dict[str, Any], right: dict[str, Any]) -> bool:
    try:
        left_model = WorkoutIn(**left, sets=[])
        right_model = WorkoutIn(**right, sets=[])
    except ValidationError:
        return False
    return left_model.model_dump(exclude={"sets"}) == right_model.model_dump(exclude={"sets"})


def _normalise_headers(reader: csv.DictReader) -> list[str]:
    headers = [header.strip().lower() for header in (reader.fieldnames or []) if header is not None]
    if len(headers) != len(set(headers)):
        raise ValueError("Le fichier contient des noms de colonnes en double.")
    reader.fieldnames = headers
    return headers


def parse_csv_import(decoded: str) -> CsvImportPlan:
    if "\x00" in decoded:
        raise ValueError("Le fichier CSV contient un caractère nul interdit.")
    try:
        dialect = csv.Sniffer().sniff(decoded[:4096], delimiters=",;")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(decoded, newline=""), dialect=dialect, strict=True)
    headers = _normalise_headers(reader)
    is_complete_export = "record_type" in headers
    if not is_complete_export:
        missing = LEGACY_REQUIRED_FIELDS - set(headers)
        if missing:
            raise ValueError(f"Colonnes obligatoires manquantes : {', '.join(sorted(missing))}")

    plan = CsvImportPlan()
    groups: dict[str, _WorkoutGroup] = {}
    saw_data_row = False
    try:
        for row_index, row in enumerate(reader, start=2):
            line_no = reader.line_num or row_index
            if not any(value for key, value in row.items() if key is not None):
                continue
            saw_data_row = True
            if None in row:
                plan.rejected_rows += 1
                plan.errors.append(f"Ligne {line_no} : nombre de colonnes incorrect.")
                continue
            record_type = _text(row, "record_type", strip=True).lower() if is_complete_export else "training_set"
            if record_type not in SUPPORTED_RECORD_TYPES:
                plan.rejected_rows += 1
                plan.errors.append(f"Ligne {line_no} : type d'enregistrement inconnu « {record_type} ».")
                continue
            if record_type in {"metadata", "profile", "import"}:
                plan.ignored_rows += 1
                continue
            try:
                if record_type == "goal":
                    plan.goals.append(_goal_data(row))
                    plan.imported_rows += 1
                    continue

                workout_data = _workout_data(row)
                parsed_set = _set_data(row, legacy=not is_complete_export) if record_type == "training_set" else None
                WorkoutIn(**workout_data, sets=[])
                workout_key = _text(row, "workout_id", strip=True)
                if not workout_key:
                    workout_key = f"{workout_data['date']}\x1f{workout_data['title']}"
                group = groups.get(workout_key)
                if group is None:
                    group = _WorkoutGroup(data=workout_data)
                    groups[workout_key] = group
                elif not _metadata_matches(group.data, workout_data):
                    raise ValueError("les métadonnées de la séance diffèrent des lignes précédentes")

                if record_type == "workout":
                    if group.counted_workout_row:
                        raise ValueError("la séance est déclarée plusieurs fois")
                    group.counted_workout_row = True
                else:
                    if parsed_set is None:  # Garde de typage, impossible après la sélection du record_type.
                        raise ValueError("série d'entraînement absente")
                    group.sets.append(parsed_set)
                plan.imported_rows += 1
            except ValidationError as exc:
                plan.rejected_rows += 1
                plan.errors.append(_validation_message(line_no, exc))
            except (TypeError, ValueError):
                plan.rejected_rows += 1
                plan.errors.append(f"Ligne {line_no} : valeur ou structure invalide.")
    except csv.Error as exc:
        raise ValueError(f"Structure CSV invalide à proximité de la ligne {reader.line_num}.") from exc

    if not saw_data_row:
        raise ValueError("Le fichier CSV ne contient aucune ligne de données.")
    for group in groups.values():
        try:
            plan.workouts.append(WorkoutIn(**group.data, sets=group.sets))
        except ValidationError as exc:
            plan.rejected_rows += 1
            plan.errors.append(_validation_message(0, exc).replace("Ligne 0", "Séance regroupée"))
    return plan
