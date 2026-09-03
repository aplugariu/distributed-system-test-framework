from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./devices.db"
    redis_url: str = "redis://localhost:6379/0"
    queue_enabled: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
