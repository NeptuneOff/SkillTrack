from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "SkillTrack API"
    environment: str = "development"
    database_url: str = Field(default="sqlite:///./skilltrack.db", alias="DATABASE_URL")
    jwt_secret: str = Field(default="dev-secret-change-me", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=120, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")
    mail_host: str = Field(default="localhost", alias="MAIL_HOST")
    mail_port: int = Field(default=1025, alias="MAIL_PORT")
    mail_from: str = Field(default="no-reply@skilltrack.local", alias="MAIL_FROM")
    import_async_threshold_rows: int = Field(default=1000, alias="IMPORT_ASYNC_THRESHOLD_ROWS")
    import_async_threshold_bytes: int = Field(default=2_097_152, alias="IMPORT_ASYNC_THRESHOLD_BYTES")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
