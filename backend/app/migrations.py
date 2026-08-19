from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from app.core.config import settings

INITIALISATION_LOCK_ID = 831_574_225


@contextmanager
def database_initialisation_lock() -> Iterator[None]:
    """Sérialise migration et seed lorsque plusieurs workers démarrent ensemble."""
    if not settings.database_url.startswith("postgresql"):
        yield
        return
    lock_engine = create_engine(settings.database_url, pool_pre_ping=True)
    try:
        with lock_engine.connect() as connection:
            connection.execute(text("SELECT pg_advisory_lock(:lock_id)"), {"lock_id": INITIALISATION_LOCK_ID})
            try:
                yield
            finally:
                connection.execute(text("SELECT pg_advisory_unlock(:lock_id)"), {"lock_id": INITIALISATION_LOCK_ID})
    finally:
        lock_engine.dispose()


def run_migrations() -> None:
    app_root = Path(__file__).resolve().parent
    config = Config(str(app_root / "alembic.ini"))
    config.set_main_option("script_location", str(app_root / "alembic"))
    config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
    command.upgrade(config, "head")
