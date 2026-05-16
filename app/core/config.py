from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    PROJECT_NAME: str = 'Python Async Template'
    API_V1_STR: str = '/api/v1'
    ENV: str = 'local'
    LOG_LEVEL: str = 'INFO'

    POSTGRES_USER: str = 'app'
    POSTGRES_PASSWORD: str = 'app'
    POSTGRES_HOST: str = 'db'
    POSTGRES_PORT: str = '5432'
    POSTGRES_DB: str = 'app'
    DB_ECHO_LOG: bool = False

    REDIS_HOST: str = 'redis'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ''

    SENTRY_DSN: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.0

    BACKEND_CORS_ORIGINS: list[str] = ['http://localhost:8000']

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:  # noqa: N802
        return (
            f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )

    @property
    def REDIS_URL(self) -> str:  # noqa: N802
        auth = f':{self.REDIS_PASSWORD}@' if self.REDIS_PASSWORD else ''
        return f'redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}'


settings = Settings()
