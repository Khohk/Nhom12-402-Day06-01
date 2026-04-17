from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PORT: int = 8000
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""
    AGENT_API_KEY: str = ""
    LOG_LEVEL: str = "INFO"
    RATE_LIMIT_PER_MINUTE: int = 10
    MONTHLY_BUDGET_USD: float = 10.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
