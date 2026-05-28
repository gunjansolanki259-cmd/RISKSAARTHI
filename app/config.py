from pydantic_settings import BaseSettings
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    IDENTITY_SALT: str

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
