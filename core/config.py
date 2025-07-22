from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    JWT_SECRET_KEY: str = 'jwt-secret-key'


settings = Settings()
