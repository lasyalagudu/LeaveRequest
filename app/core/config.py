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

     # ✅ Holidays API settings
    COUNTRY: str = "IN"        # <-- add this
    API_KEY: str               # <-- add this if you want to keep API key here

    @property
    def DATABASE_URL(self) -> str:
        # Use this for Postgres:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        # For quick local SQLite testing, comment the above and use:
        # return "sqlite:///./leave.db"

    class Config:
        env_file = ".env"

settings = Settings()
