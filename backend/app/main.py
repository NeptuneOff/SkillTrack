from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, health, import_export, stats, workouts
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.logging import configure_logging
from app.core.security import hash_password
from app.models import User
from app.core.database import SessionLocal
from sqlalchemy import select

configure_logging()
settings = get_settings()

Base.metadata.create_all(bind=engine)


def seed_demo_user() -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.email == "demo@skilltrack.local"))
        if existing is None:
            db.add(User(email="demo@skilltrack.local", display_name="Demo", password_hash=hash_password("DemoPassword123!")))
            db.commit()
    finally:
        db.close()


seed_demo_user()

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(workouts.router)
app.include_router(stats.router)
app.include_router(import_export.router)
