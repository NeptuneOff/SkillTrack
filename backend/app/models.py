from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def uid() -> str:
    return str(uuid4())


def utc_now_naive() -> datetime:
    """UTC sans fuseau pour rester compatible avec les volumes DateTime historiques."""
    return datetime.now(UTC).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)
    workouts: Mapped[list[Workout]] = relationship(
        back_populates="owner", cascade="all, delete-orphan", passive_deletes=True
    )
    goals: Mapped[list[Goal]] = relationship(
        back_populates="owner", cascade="all, delete-orphan", passive_deletes=True
    )
    imports: Mapped[list[ImportJob]] = relationship(
        back_populates="owner", cascade="all, delete-orphan", passive_deletes=True
    )


class Workout(Base):
    __tablename__ = "workouts"
    __table_args__ = (
        CheckConstraint("intensity BETWEEN 1 AND 10", name="ck_workouts_intensity"),
        CheckConstraint("duration_minutes BETWEEN 1 AND 1440", name="ck_workouts_duration_minutes"),
        Index("ix_workouts_owner_date", "owner_id", "date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    date: Mapped[date] = mapped_column(Date)
    type: Mapped[str] = mapped_column(String(80), default="Technique")
    intensity: Mapped[int] = mapped_column(Integer, default=6)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)
    owner: Mapped[User] = relationship(back_populates="workouts")
    sets: Mapped[list[TrainingSet]] = relationship(
        back_populates="workout",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by=lambda: (TrainingSet.position, TrainingSet.id),
    )


class TrainingSet(Base):
    __tablename__ = "training_sets"
    __table_args__ = (
        CheckConstraint("set_count BETWEEN 1 AND 50", name="ck_training_sets_set_count"),
        CheckConstraint("reps BETWEEN 0 AND 1000", name="ck_training_sets_reps"),
        CheckConstraint("load_kg BETWEEN 0 AND 1000", name="ck_training_sets_load_kg"),
        CheckConstraint("duration_seconds BETWEEN 0 AND 86400", name="ck_training_sets_duration_seconds"),
        CheckConstraint("difficulty BETWEEN 1 AND 10", name="ck_training_sets_difficulty"),
        CheckConstraint("assistance_kg BETWEEN 0 AND 1000", name="ck_training_sets_assistance_kg"),
        CheckConstraint("position >= 0", name="ck_training_sets_position"),
        UniqueConstraint("workout_id", "position", name="uq_training_sets_workout_position"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    workout_id: Mapped[str] = mapped_column(ForeignKey("workouts.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    exercise: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(40), default="autre")
    set_count: Mapped[int] = mapped_column(Integer, default=1)
    reps: Mapped[int] = mapped_column(Integer, default=0)
    load_kg: Mapped[float] = mapped_column(Float, default=0)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    difficulty: Mapped[int] = mapped_column(Integer, default=5)
    assistance_kg: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    workout: Mapped[Workout] = relationship(back_populates="sets")


class Goal(Base):
    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint("current_value >= 0", name="ck_goals_current_value"),
        CheckConstraint("target_value > 0", name="ck_goals_target_value"),
        CheckConstraint("priority IN ('basse', 'moyenne', 'haute')", name="ck_goals_priority"),
        CheckConstraint("status IN ('actif', 'termine', 'archive')", name="ck_goals_status"),
        CheckConstraint("is_done = (status = 'termine')", name="ck_goals_completion_consistency"),
        Index("ix_goals_owner_status", "owner_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    skill: Mapped[str] = mapped_column(String(120))
    goal_type: Mapped[str] = mapped_column(String(40), default="figure")
    target: Mapped[str] = mapped_column(String(160))
    current_level: Mapped[str] = mapped_column(String(160), default="Début")
    current_value: Mapped[float] = mapped_column(Float, default=0)
    target_value: Mapped[float] = mapped_column(Float, default=1)
    unit: Mapped[str] = mapped_column(String(40), default="autre")
    priority: Mapped[str] = mapped_column(String(20), default="moyenne")
    notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="actif")
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    owner: Mapped[User] = relationship(back_populates="goals")


class ImportJob(Base):
    __tablename__ = "import_jobs"
    __table_args__ = (
        CheckConstraint("imported_rows >= 0", name="ck_import_jobs_imported_rows"),
        CheckConstraint("rejected_rows >= 0", name="ck_import_jobs_rejected_rows"),
        CheckConstraint("ignored_rows >= 0", name="ck_import_jobs_ignored_rows"),
        Index("ix_import_jobs_owner_created", "owner_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    imported_rows: Mapped[int] = mapped_column(Integer, default=0)
    rejected_rows: Mapped[int] = mapped_column(Integer, default=0)
    ignored_rows: Mapped[int] = mapped_column(Integer, default=0)
    report: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)
    owner: Mapped[User] = relationship(back_populates="imports")
