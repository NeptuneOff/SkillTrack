from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./skilltrack.db"
    secret_key: str = "dev-secret"
    access_token_expire_minutes: int = 1440
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    mailhog_host: str = "mailhog"
    mailhog_port: int = 1025
    demo_email: str = "demo@skilltrack.dev"
    demo_password: str = "DemoPassword123!"

settings = Settings()
