from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "FastAPI Backend"
    app_version: str = "1.0.0"
    debug: bool = True
    api_v1_str: str = "/api/v1"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ai22"

    class Config:
        env_file = ".env"


settings = Settings()
