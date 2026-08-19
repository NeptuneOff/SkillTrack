from datetime import date, timedelta
from typing import Any
from sqlalchemy.orm import Session, joinedload
from app.models import Workout, TrainingSet, Goal, User
from app.schemas import WorkoutIn

def workout_volume(workout: Workout) -> float:
    total = 0.0
    for s in workout.sets:
        total += (s.set_count or 1) * ((s.reps or 0) * max((s.load_kg or 0) - (s.assistance_kg or 0), 1) + (s.duration_seconds or 0) * 0.2)
    return round(total, 2)

def make_workout_out(w: Workout) -> dict:
    return {
        "id": w.id,
        "title": w.title,
        "date": w.date,
        "type": w.type,
        "intensity": w.intensity,
        "duration_minutes": w.duration_minutes,
        "notes": w.notes,
        "sets": w.sets,
        "volume": workout_volume(w),
    }

def create_workout(db: Session, user: User, data: WorkoutIn) -> Workout:
    w = Workout(owner_id=user.id, title=data.title, date=data.date, type=data.type, intensity=data.intensity, duration_minutes=data.duration_minutes, notes=data.notes)
    for s in data.sets:
        w.sets.append(TrainingSet(**s.model_dump()))
    db.add(w); db.commit(); db.refresh(w)
    return w

def update_workout(db: Session, w: Workout, data: WorkoutIn) -> Workout:
    for k, v in data.model_dump(exclude={"sets"}).items(): setattr(w, k, v)
    w.sets.clear(); db.flush()
    for s in data.sets: w.sets.append(TrainingSet(**s.model_dump()))
    db.commit(); db.refresh(w)
    return w

def dashboard(db: Session, user: User) -> dict:
    workouts = db.query(Workout).options(joinedload(Workout.sets)).filter(Workout.owner_id == user.id).order_by(Workout.date.desc()).all()
    goals = db.query(Goal).filter(Goal.owner_id == user.id).order_by(Goal.is_done.asc()).all()
    total_volume = sum(workout_volume(w) for w in workouts)
    set_count = sum(len(w.sets) for w in workouts)
    total_duration = sum(w.duration_minutes for w in workouts)
    avg_intensity = round(sum(w.intensity for w in workouts) / len(workouts), 2) if workouts else 0
    exercise_count = len({s.exercise.strip().lower() for w in workouts for s in w.sets})
    today = date.today()
    weekly: list[dict[str, Any]] = []
    for i in range(7, -1, -1):
        start = today - timedelta(days=today.weekday() + i*7)
        end = start + timedelta(days=6)
        vol = sum(workout_volume(w) for w in workouts if start <= w.date <= end)
        weekly.append({"week": start.isoformat(), "volume": round(vol, 2)})
    current_week = weekly[-1]["volume"] if weekly else 0
    previous_week = weekly[-2]["volume"] if len(weekly) > 1 else 0
    progress = round(((current_week - previous_week) / previous_week) * 100, 1) if previous_week else (100.0 if current_week else 0.0)
    return {
        "workout_count": len(workouts), "set_count": set_count, "total_volume": round(total_volume, 2),
        "total_duration_minutes": total_duration, "average_intensity": avg_intensity,
        "weekly_volume": weekly, "recent_workouts": [make_workout_out(w) for w in workouts[:5]], "goals": goals,
        "exercise_count": exercise_count, "last_workout": make_workout_out(workouts[0]) if workouts else None,
        "recent_progress_percent": progress,
    }
