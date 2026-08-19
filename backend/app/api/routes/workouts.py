from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.core.errors import NotFoundError
from app.schemas import WorkoutCreate, WorkoutRead, WorkoutUpdate
from app.services.workout_service import WorkoutService

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.get("", response_model=list[WorkoutRead])
def list_workouts(db: DbSession, current_user: CurrentUser) -> list[WorkoutRead]:
    return WorkoutService(db).list_workouts(current_user.id)


@router.post("", response_model=WorkoutRead, status_code=status.HTTP_201_CREATED)
def create_workout(payload: WorkoutCreate, db: DbSession, current_user: CurrentUser) -> WorkoutRead:
    return WorkoutService(db).create_workout(current_user.id, payload)


@router.get("/{workout_id}", response_model=WorkoutRead)
def get_workout(workout_id: str, db: DbSession, current_user: CurrentUser) -> WorkoutRead:
    try:
        return WorkoutService(db).get_required(workout_id, current_user.id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{workout_id}", response_model=WorkoutRead)
def update_workout(workout_id: str, payload: WorkoutUpdate, db: DbSession, current_user: CurrentUser) -> WorkoutRead:
    try:
        return WorkoutService(db).update_workout(workout_id, current_user.id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: str, db: DbSession, current_user: CurrentUser) -> None:
    try:
        WorkoutService(db).delete_workout(workout_id, current_user.id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
