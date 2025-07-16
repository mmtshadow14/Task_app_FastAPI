from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///sqlite.db'
    JWT_SECRET_KEY: str = 'jwt-secret-key'


settings = Settings()
