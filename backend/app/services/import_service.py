import csv
import hashlib
import io
import json
from datetime import UTC, datetime, date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import ExerciseSet, ImportJob, ImportStatus, Workout, WorkoutExercise
from app.schemas import ImportResult

REQUIRED_COLUMNS = {"date", "workout_title", "exercise", "reps", "external_load_kg"}


class WorkoutImportService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def import_csv(self, user_id: str, file_name: str, content: bytes) -> ImportResult:
        file_hash = hashlib.sha256(content).hexdigest()
        text = self._decode(content)
        reader = csv.DictReader(io.StringIO(text))
        if reader.fieldnames is None:
            return ImportResult(mode="sync", rows_read=0, rows_accepted=0, rows_rejected=1, errors=[{"row": 0, "error": "empty_file"}])
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            return ImportResult(
                mode="sync",
                rows_read=0,
                rows_accepted=0,
                rows_rejected=1,
                errors=[{"row": 0, "error": "missing_columns", "columns": sorted(missing)}],
            )
        rows = list(reader)
        mode = "async" if len(rows) > self.settings.import_async_threshold_rows or len(content) > self.settings.import_async_threshold_bytes else "sync"
        job = ImportJob(user_id=user_id, file_name=file_name, file_hash=file_hash, status=ImportStatus.running, rows_read=len(rows))
        self.db.add(job)
        try:
            self.db.flush()
        except IntegrityError:
            self.db.rollback()
            return ImportResult(mode=mode, rows_read=len(rows), rows_accepted=0, rows_rejected=0, errors=[{"row": 0, "error": "duplicate_import"}])

        accepted, errors = self._persist_rows(user_id, rows)
        job.rows_accepted = accepted
        job.rows_rejected = len(errors)
        job.status = ImportStatus.completed if not errors else ImportStatus.completed_with_errors
        job.error_report = json.dumps(errors, ensure_ascii=False)
        job.finished_at = datetime.now(UTC)
        self.db.commit()
        return ImportResult(mode=mode, job_id=job.id, rows_read=len(rows), rows_accepted=accepted, rows_rejected=len(errors), errors=errors)

    def _decode(self, content: bytes) -> str:
        for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError("Unsupported encoding")

    def _persist_rows(self, user_id: str, rows: list[dict[str, str]]) -> tuple[int, list[dict[str, object]]]:
        accepted = 0
        errors: list[dict[str, object]] = []
        grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
        for index, row in enumerate(rows, start=2):
            error = self._validate_row(row)
            if error:
                errors.append({"row": index, "error": error})
                continue
            grouped.setdefault((row["date"], row["workout_title"]), []).append(row)
        for (performed_on, title), group in grouped.items():
            workout = Workout(user_id=user_id, title=title.strip(), performed_on=date.fromisoformat(performed_on))
            exercises_by_name: dict[str, WorkoutExercise] = {}
            for row in group:
                exercise = exercises_by_name.get(row["exercise"])
                if exercise is None:
                    exercise = WorkoutExercise(name=row["exercise"].strip(), position=len(exercises_by_name))
                    exercises_by_name[row["exercise"]] = exercise
                    workout.exercises.append(exercise)
                exercise.sets.append(
                    ExerciseSet(
                        reps=int(row["reps"]),
                        external_load_kg=float(row.get("external_load_kg") or 0),
                        hold_seconds=int(row["hold_seconds"]) if row.get("hold_seconds") else None,
                        rpe=int(row["rpe"]) if row.get("rpe") else None,
                    )
                )
                accepted += 1
            self.db.add(workout)
        return accepted, errors

    def _validate_row(self, row: dict[str, str]) -> str | None:
        try:
            datetime.strptime(row["date"], "%Y-%m-%d")
        except ValueError:
            return "invalid_date"
        if not row["workout_title"].strip():
            return "missing_workout_title"
        if not row["exercise"].strip():
            return "missing_exercise"
        try:
            reps = int(row["reps"])
            load = float(row.get("external_load_kg") or 0)
        except ValueError:
            return "invalid_number"
        if reps < 0 or load < 0:
            return "negative_value"
        return None
