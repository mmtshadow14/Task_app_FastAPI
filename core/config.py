from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = True
    POSTGRESQL_DATABASE_URI: str = "postgres://postgres:postgres@db/postgres"
    JWT_SECRET_KEY: str = 'jwt-secret-key'


settings = Settings()
