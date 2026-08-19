import csv
import io
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.repositories.workouts import WorkoutRepository


class ExportService:
    def __init__(self, db: Session):
        self.db = db
        self.workouts = WorkoutRepository(db)

    def workouts_csv(self, user_id: str) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["workout_id", "date", "title", "exercise", "variation", "reps", "external_load_kg", "hold_seconds", "rpe"])
        for workout in self.workouts.list_by_user(user_id):
            for exercise in workout.exercises:
                for set_ in exercise.sets:
                    writer.writerow([
                        workout.id,
                        workout.performed_on.isoformat(),
                        workout.title,
                        exercise.name,
                        exercise.variation or "",
                        set_.reps,
                        float(set_.external_load_kg),
                        set_.hold_seconds or "",
                        set_.rpe or "",
                    ])
        return output.getvalue()

    def workouts_json(self, user_id: str) -> dict[str, object]:
        workouts = []
        for workout in self.workouts.list_by_user(user_id):
            workouts.append(
                {
                    "id": workout.id,
                    "date": workout.performed_on.isoformat(),
                    "title": workout.title,
                    "notes": workout.notes,
                    "exercises": [
                        {
                            "name": exercise.name,
                            "variation": exercise.variation,
                            "sets": [
                                {
                                    "reps": set_.reps,
                                    "external_load_kg": float(set_.external_load_kg),
                                    "hold_seconds": set_.hold_seconds,
                                    "rpe": set_.rpe,
                                }
                                for set_ in exercise.sets
                            ],
                        }
                        for exercise in workout.exercises
                    ],
                }
            )
        return {"generated_at": datetime.now(UTC).isoformat(), "workouts": workouts}
