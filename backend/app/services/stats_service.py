from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ExerciseSet, Workout, WorkoutExercise
from app.schemas import WeeklyVolumePoint


class StatsService:
    def __init__(self, db: Session):
        self.db = db

    def weekly_volume(self, user_id: str) -> list[WeeklyVolumePoint]:
        week_expr = func.to_char(func.date_trunc("week", Workout.performed_on), "IYYY-IW")
        # SQLite fallback for local tests without PostgreSQL.
        if self.db.bind is not None and self.db.bind.dialect.name == "sqlite":
            week_expr = func.strftime("%Y-%W", Workout.performed_on)
        stmt = (
            select(
                week_expr.label("week"),
                WorkoutExercise.name.label("exercise_name"),
                func.count(ExerciseSet.id).label("total_sets"),
                func.coalesce(func.sum(ExerciseSet.reps), 0).label("total_reps"),
                func.coalesce(func.sum(ExerciseSet.reps * ExerciseSet.external_load_kg), 0).label("external_volume_kg"),
            )
            .join(WorkoutExercise, WorkoutExercise.workout_id == Workout.id)
            .join(ExerciseSet, ExerciseSet.exercise_id == WorkoutExercise.id)
            .where(Workout.user_id == user_id)
            .group_by(week_expr, WorkoutExercise.name)
            .order_by(week_expr, WorkoutExercise.name)
        )
        return [
            WeeklyVolumePoint(
                week=str(row.week),
                exercise_name=row.exercise_name,
                total_sets=int(row.total_sets),
                total_reps=int(row.total_reps),
                external_volume_kg=float(row.external_volume_kg),
            )
            for row in self.db.execute(stmt).all()
        ]
