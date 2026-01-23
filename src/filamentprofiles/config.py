"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql://filamentprofiles:changeme@localhost:5432/filamentprofiles"
    spoolman_url: str | None = None
    slicer_profile_path: str | None = None
    spoolmandb_cache_ttl: int = 86400  # 24 hours in seconds

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
