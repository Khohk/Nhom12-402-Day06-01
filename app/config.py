from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PORT: int = 8000
    REDIS_URL: str = "redis://localhost:6379"
    AGENT_API_KEY: str = ""
    LOG_LEVEL: str = "INFO"
    RATE_LIMIT_PER_MINUTE: int = 20
    MONTHLY_BUDGET_USD: float = 50.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
