import os

from pydantic_settings import BaseSettings

DATABASE_URL = os.getenv("DATABASE_URL")


class Settings(BaseSettings):
    DEBUG: bool = True
    DATABASE_URL: str = DATABASE_URL
    JWT_SECRET_KEY: str = 'jwt-secret-key'


settings = Settings()
