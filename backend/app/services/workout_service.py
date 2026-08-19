from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models import ExerciseSet, Workout, WorkoutExercise
from app.repositories.workouts import WorkoutRepository
from app.schemas import WorkoutCreate, WorkoutUpdate


class WorkoutService:
    def __init__(self, db: Session):
        self.db = db
        self.workouts = WorkoutRepository(db)

    def list_workouts(self, user_id: str) -> list[Workout]:
        return self.workouts.list_by_user(user_id)

    def create_workout(self, user_id: str, payload: WorkoutCreate) -> Workout:
        workout = Workout(
            user_id=user_id,
            title=payload.title.strip(),
            performed_on=payload.performed_on,
            notes=payload.notes,
        )
        for exercise_payload in payload.exercises:
            exercise = WorkoutExercise(
                name=exercise_payload.name.strip(),
                variation=exercise_payload.variation,
                position=exercise_payload.position,
            )
            exercise.sets = [
                ExerciseSet(
                    reps=set_payload.reps,
                    external_load_kg=set_payload.external_load_kg,
                    hold_seconds=set_payload.hold_seconds,
                    rpe=set_payload.rpe,
                )
                for set_payload in exercise_payload.sets
            ]
            workout.exercises.append(exercise)
        self.workouts.add(workout)
        self.db.commit()
        self.db.refresh(workout)
        return workout

    def get_required(self, workout_id: str, user_id: str) -> Workout:
        workout = self.workouts.get_by_user(workout_id, user_id)
        if workout is None:
            raise NotFoundError("Workout not found")
        return workout

    def update_workout(self, workout_id: str, user_id: str, payload: WorkoutUpdate) -> Workout:
        workout = self.get_required(workout_id, user_id)
        if payload.title is not None:
            workout.title = payload.title.strip()
        if payload.performed_on is not None:
            workout.performed_on = payload.performed_on
        if payload.notes is not None:
            workout.notes = payload.notes
        self.db.commit()
        self.db.refresh(workout)
        return workout

    def delete_workout(self, workout_id: str, user_id: str) -> None:
        workout = self.get_required(workout_id, user_id)
        self.workouts.delete(workout)
        self.db.commit()
