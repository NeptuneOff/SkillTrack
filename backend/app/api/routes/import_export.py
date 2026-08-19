from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse

from app.api.deps import CurrentUser, DbSession
from app.schemas import ImportResult
from app.services.export_service import ExportService
from app.services.import_service import WorkoutImportService

router = APIRouter(tags=["import-export"])


@router.post("/imports/workouts", response_model=ImportResult)
async def import_workouts(db: DbSession, current_user: CurrentUser, file: UploadFile = File(...)) -> ImportResult:
    content = await file.read()
    return WorkoutImportService(db).import_csv(current_user.id, file.filename or "workouts.csv", content)


@router.get("/exports/workouts.csv")
def export_workouts_csv(db: DbSession, current_user: CurrentUser) -> PlainTextResponse:
    csv_text = ExportService(db).workouts_csv(current_user.id)
    return PlainTextResponse(csv_text, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=skilltrack_workouts.csv"})


@router.get("/exports/workouts.json")
def export_workouts_json(db: DbSession, current_user: CurrentUser) -> JSONResponse:
    return JSONResponse(ExportService(db).workouts_json(current_user.id))
