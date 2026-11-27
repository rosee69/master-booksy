from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str
    test_database_url: str | None = None
    debug: bool = False
    timezone: str = "Asia/Bangkok"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """Create application settings from environment variables."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
