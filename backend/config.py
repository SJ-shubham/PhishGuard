from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db:  str = "phishguard"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # JWT
    jwt_secret:                  str = "change-this-secret"
    jwt_algorithm:               str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days:   int = 7

    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # Rate limiting
    rate_limit_scans_per_minute: int = 10

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
