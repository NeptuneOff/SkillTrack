from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Workout, WorkoutExercise


class WorkoutRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, user_id: str) -> list[Workout]:
        stmt = (
            select(Workout)
            .options(selectinload(Workout.exercises).selectinload(WorkoutExercise.sets))
            .where(Workout.user_id == user_id)
            .order_by(Workout.performed_on.desc(), Workout.created_at.desc())
        )
        return list(self.db.scalars(stmt).unique())

    def get_by_user(self, workout_id: str, user_id: str) -> Workout | None:
        stmt = (
            select(Workout)
            .options(selectinload(Workout.exercises).selectinload(WorkoutExercise.sets))
            .where(Workout.id == workout_id, Workout.user_id == user_id)
        )
        return self.db.scalar(stmt)

    def add(self, workout: Workout) -> Workout:
        self.db.add(workout)
        self.db.flush()
        return workout

    def delete(self, workout: Workout) -> None:
        self.db.delete(workout)
        self.db.flush()
