from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PositiveInt = Annotated[int, Field(ge=0, le=10_000)]
LoadKg = Annotated[float, Field(ge=0, le=500)]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    display_name: str = Field(min_length=2, max_length=120)

    @field_validator("password")
    @classmethod
    def strong_enough(cls, value: str) -> str:
        if value.lower() == value or value.upper() == value or not any(char.isdigit() for char in value):
            raise ValueError("Password must include uppercase, lowercase and digit")
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    display_name: str
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ExerciseSetCreate(BaseModel):
    reps: PositiveInt
    external_load_kg: LoadKg = 0
    hold_seconds: int | None = Field(default=None, ge=0, le=600)
    rpe: int | None = Field(default=None, ge=1, le=10)


class ExerciseSetRead(ExerciseSetCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str


class WorkoutExerciseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    variation: str | None = Field(default=None, max_length=120)
    position: int = Field(default=0, ge=0, le=100)
    sets: list[ExerciseSetCreate] = Field(default_factory=list)


class WorkoutExerciseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    variation: str | None
    position: int
    sets: list[ExerciseSetRead]


class WorkoutCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    performed_on: date
    notes: str | None = Field(default=None, max_length=2000)
    exercises: list[WorkoutExerciseCreate] = Field(default_factory=list)


class WorkoutUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    performed_on: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class WorkoutRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    performed_on: date
    notes: str | None
    exercises: list[WorkoutExerciseRead]


class SkillProgressCreate(BaseModel):
    skill_name: str = Field(min_length=1, max_length=120)
    variation: str | None = Field(default=None, max_length=120)
    measured_on: date
    hold_seconds: int | None = Field(default=None, ge=0, le=600)
    quality_score: int | None = Field(default=None, ge=1, le=10)
    notes: str | None = Field(default=None, max_length=2000)


class SkillProgressRead(SkillProgressCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str


class WeeklyVolumePoint(BaseModel):
    week: str
    exercise_name: str
    total_sets: int
    total_reps: int
    external_volume_kg: float


class ImportPreviewRow(BaseModel):
    row_number: int
    valid: bool
    errors: list[str] = Field(default_factory=list)


class ImportResult(BaseModel):
    mode: str
    job_id: str | None = None
    rows_read: int
    rows_accepted: int
    rows_rejected: int
    errors: list[dict[str, object]] = Field(default_factory=list)


class ExportBundle(BaseModel):
    workouts: list[WorkoutRead]
    generated_at: datetime
