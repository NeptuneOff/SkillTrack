from __future__ import annotations
from datetime import date, datetime
from uuid import uuid4
from sqlalchemy import String, Date, DateTime, Integer, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

def uid() -> str:
    return str(uuid4())

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    workouts: Mapped[list[Workout]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    goals: Mapped[list[Goal]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class Workout(Base):
    __tablename__ = "workouts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    date: Mapped[date] = mapped_column(Date)
    type: Mapped[str] = mapped_column(String(80), default="Technique")
    intensity: Mapped[int] = mapped_column(Integer, default=6)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    owner: Mapped[User] = relationship(back_populates="workouts")
    sets: Mapped[list[TrainingSet]] = relationship(back_populates="workout", cascade="all, delete-orphan")

class TrainingSet(Base):
    __tablename__ = "training_sets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    workout_id: Mapped[str] = mapped_column(ForeignKey("workouts.id", ondelete="CASCADE"), index=True)
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
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    imported_rows: Mapped[int] = mapped_column(Integer, default=0)
    rejected_rows: Mapped[int] = mapped_column(Integer, default=0)
    report: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
