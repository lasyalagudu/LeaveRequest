# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "leave_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    APP_ENV: str = "dev"
    APP_PORT: int = 8000

    DEFAULT_ANNUAL_ALLOCATION: int = 24

    COUNTRY: str = "IN"
    API_KEY: str  # holidays API

    # ✅ SMTP configuration
    SMTP_SERVER: str = "smtp.gmail.com"       # SMTP host
    SMTP_PORT: int = 587                       # TLS port
    SMTP_USERNAME: str = "lasyalagudu@gmail.com"
    SMTP_PASSWORD: str = "tskf rcls wiqf qmpa"   # use App Password if Gmail
    SMTP_FROM: str = "lasyalagudu@gmail.com"
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"

settings = Settings()
