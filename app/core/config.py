import enum
from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMProvider(str, enum.Enum):
    OPENAI = "openai"
    GEMINI = "gemini"

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    REDIS_HOST: str
    REDIS_PORT: int = 6379

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    OPENAI_API_KEY: str = ""
    LLM_PROVIDER: LLMProvider = LLMProvider.OPENAI
    CLASSIFICATION_BATCH_SIZE: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
