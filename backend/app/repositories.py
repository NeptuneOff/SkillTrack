from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Protocol

from fastapi import Depends
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import Goal, ImportJob, TrainingSet, User, Workout


class SkillTrackRepository(Protocol):
    """Storage port used by the API and business services.

    The protocol keeps query details outside route handlers and makes the
    persistence adapter replaceable in focused unit tests or a future store.
    """

    def user_by_email(self, email: str) -> User | None: ...

    def user_by_id(self, user_id: str) -> User | None: ...

    def workouts_for_owner(self, owner_id: str) -> list[Workout]: ...

    def workout_for_owner(self, owner_id: str, workout_id: str) -> Workout | None: ...

    def goals_for_owner(self, owner_id: str, *, active_only: bool = False) -> list[Goal]: ...

    def goal_for_owner(self, owner_id: str, goal_id: str) -> Goal | None: ...

    def imports_for_owner(self, owner_id: str, *, limit: int | None = None) -> list[ImportJob]: ...

    def import_for_owner(self, owner_id: str, job_id: str) -> ImportJob | None: ...

    def owned_counts(self, owner_id: str) -> dict[str, int]: ...

    def add(self, entity: Any) -> None: ...

    def add_all(self, entities: Iterable[Any]) -> None: ...

    def delete(self, entity: Any) -> None: ...

    def flush(self) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def refresh(self, entity: Any) -> None: ...


class SqlAlchemySkillTrackRepository:
    """SQLAlchemy/PostgreSQL adapter for the application storage port."""

    def __init__(self, session: Session):
        self.session = session

    def user_by_email(self, email: str) -> User | None:
        return self.session.query(User).filter(User.email == email).first()

    def user_by_id(self, user_id: str) -> User | None:
        return self.session.get(User, user_id)

    def workouts_for_owner(self, owner_id: str) -> list[Workout]:
        return (
            self.session.query(Workout)
            .options(joinedload(Workout.sets))
            .filter(Workout.owner_id == owner_id)
            .order_by(Workout.date.desc(), Workout.created_at.desc())
            .all()
        )

    def workout_for_owner(self, owner_id: str, workout_id: str) -> Workout | None:
        return (
            self.session.query(Workout)
            .options(joinedload(Workout.sets))
            .filter(Workout.id == workout_id, Workout.owner_id == owner_id)
            .first()
        )

    def goals_for_owner(self, owner_id: str, *, active_only: bool = False) -> list[Goal]:
        query = self.session.query(Goal).filter(Goal.owner_id == owner_id)
        if active_only:
            return query.filter(Goal.status == "actif").order_by(Goal.deadline.asc().nullslast(), Goal.skill.asc()).all()
        return query.order_by(Goal.is_done.asc(), Goal.skill.asc()).all()

    def goal_for_owner(self, owner_id: str, goal_id: str) -> Goal | None:
        return self.session.query(Goal).filter(Goal.id == goal_id, Goal.owner_id == owner_id).first()

    def imports_for_owner(self, owner_id: str, *, limit: int | None = None) -> list[ImportJob]:
        query = (
            self.session.query(ImportJob)
            .filter(ImportJob.owner_id == owner_id)
            .order_by(ImportJob.created_at.desc())
        )
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def import_for_owner(self, owner_id: str, job_id: str) -> ImportJob | None:
        return self.session.query(ImportJob).filter(ImportJob.id == job_id, ImportJob.owner_id == owner_id).first()

    def owned_counts(self, owner_id: str) -> dict[str, int]:
        return {
            "workouts": self.session.query(Workout).filter(Workout.owner_id == owner_id).count(),
            "training_sets": (
                self.session.query(TrainingSet).join(Workout).filter(Workout.owner_id == owner_id).count()
            ),
            "goals": self.session.query(Goal).filter(Goal.owner_id == owner_id).count(),
            "imports": self.session.query(ImportJob).filter(ImportJob.owner_id == owner_id).count(),
        }

    def add(self, entity: Any) -> None:
        self.session.add(entity)

    def add_all(self, entities: Iterable[Any]) -> None:
        self.session.add_all(list(entities))

    def delete(self, entity: Any) -> None:
        self.session.delete(entity)

    def flush(self) -> None:
        self.session.flush()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, entity: Any) -> None:
        self.session.refresh(entity)


def get_repository(db: Session = Depends(get_db)) -> SqlAlchemySkillTrackRepository:
    return SqlAlchemySkillTrackRepository(db)
