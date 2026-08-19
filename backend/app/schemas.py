from datetime import date, datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def enforce_bcrypt_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Le mot de passe ne peut pas dépasser 72 octets UTF-8.")
        return value

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    display_name: str
    created_at: datetime

class SetIn(BaseModel):
    exercise: str = Field(min_length=2, max_length=160)
    category: str = Field(default="autre", max_length=40)
    set_count: int = Field(default=1, ge=1, le=50)
    reps: int = Field(default=0, ge=0, le=1000)
    load_kg: float = Field(default=0, ge=0, le=1000)
    duration_seconds: int = Field(default=0, ge=0, le=86400)
    difficulty: int = Field(default=5, ge=1, le=10)
    assistance_kg: float = Field(default=0, ge=0, le=1000)
    notes: str = Field(default="", max_length=2000)

class SetOut(SetIn):
    model_config = ConfigDict(from_attributes=True)

    id: str

class WorkoutIn(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    date: date
    type: str = Field(default="Technique", min_length=2, max_length=80)
    intensity: int = Field(default=6, ge=1, le=10)
    duration_minutes: int = Field(default=60, ge=1, le=1440)
    notes: str = Field(default="", max_length=4000)
    sets: list[SetIn] = Field(default_factory=list)

class WorkoutOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    date: date
    type: str
    intensity: int
    duration_minutes: int
    notes: str
    sets: list[SetOut] = Field(default_factory=list)
    volume: float

class GoalIn(BaseModel):
    skill: str = Field(min_length=2, max_length=120)
    goal_type: str = Field(default="figure", max_length=40)
    target: str = Field(min_length=2, max_length=160)
    current_level: str = Field(default="Début", max_length=160)
    current_value: float = Field(default=0, ge=0)
    target_value: float = Field(default=1, gt=0)
    unit: str = Field(default="autre", max_length=40)
    priority: str = Field(default="moyenne", pattern="^(basse|moyenne|haute)$")
    notes: str = Field(default="", max_length=2000)
    status: str = Field(default="actif", pattern="^(actif|termine|archive)$")
    deadline: date | None = None
    is_done: bool = False

    @model_validator(mode="after")
    def keep_completion_fields_consistent(self) -> Self:
        self.is_done = self.status == "termine"
        return self

class GoalOut(GoalIn):
    model_config = ConfigDict(from_attributes=True)

    id: str

class DashboardOut(BaseModel):
    workout_count: int
    set_count: int
    total_volume: float
    total_duration_minutes: int
    average_intensity: float
    weekly_volume: list[dict]
    recent_workouts: list[WorkoutOut]
    goals: list[GoalOut]
    exercise_count: int
    last_workout: WorkoutOut | None
    recent_progress_percent: float
