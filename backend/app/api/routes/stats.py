from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas import WeeklyVolumePoint
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/weekly-volume", response_model=list[WeeklyVolumePoint])
def weekly_volume(db: DbSession, current_user: CurrentUser) -> list[WeeklyVolumePoint]:
    return StatsService(db).weekly_volume(current_user.id)
