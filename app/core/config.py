import secrets
import warnings
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    DATABASE_URL: str = "sqlite:///./task_manager.db"

    SECRET_KEY: str = "dev-secret-key-CHANGE-THIS-IN-PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DEBUG: bool = False          # Always False in production
    APP_NAME: str = "Team Task Manager"
    APP_VERSION: str = "0.1.0"

    PORT: int = 8000             # Railway sets $PORT automatically

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",          # ignore unknown env vars (Railway adds many)
    )

    def validate_production(self) -> None:
        if self.SECRET_KEY == "dev-secret-key-CHANGE-THIS-IN-PRODUCTION":
            warnings.warn(
                "SECRET_KEY is set to the default development value. "
                "Set a strong SECRET_KEY environment variable before deploying.",
                stacklevel=2,
            )
        if self.DEBUG:
            warnings.warn(
                "DEBUG=True in production exposes stack traces. "
                "Set DEBUG=False in your Railway environment variables.",
                stacklevel=2,
            )

settings = Settings()
settings.validate_production()
