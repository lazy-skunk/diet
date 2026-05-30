from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str = Field(serialization_alias="SECRET_KEY")
    wtf_csrf_secret_key: str = Field(serialization_alias="WTF_CSRF_SECRET_KEY")
    database_url: str = Field(
        default=f"sqlite:///{_BASE_DIR / 'local.sqlite'}",
        serialization_alias="SQLALCHEMY_DATABASE_URI",
    )
    sqlalchemy_track_modifications: bool = Field(
        default=False,
        serialization_alias="SQLALCHEMY_TRACK_MODIFICATIONS",
    )
    sqlalchemy_echo: bool = Field(
        default=True,
        serialization_alias="SQLALCHEMY_ECHO",
    )


class TestingSettings(BaseModel):
    secret_key: str = Field(
        default="testing-secret-key",
        serialization_alias="SECRET_KEY",
    )
    wtf_csrf_secret_key: str = Field(
        default="testing-csrf-secret-key",
        serialization_alias="WTF_CSRF_SECRET_KEY",
    )
    database_url: str = Field(
        default=f"sqlite:///{_BASE_DIR / 'testing.sqlite'}",
        serialization_alias="SQLALCHEMY_DATABASE_URI",
    )
    sqlalchemy_track_modifications: bool = Field(
        default=False,
        serialization_alias="SQLALCHEMY_TRACK_MODIFICATIONS",
    )
    wtf_csrf_enabled: bool = Field(
        default=False,
        serialization_alias="WTF_CSRF_ENABLED",
    )


class LogSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    log_level: str = "DEBUG"
    log_path: str = "log/app.log"
    log_size: int = 1024 * 1024 * 10
    log_backup: int = 3


_log_settings = LogSettings()


def get_config(config_key: str) -> dict[str, object]:
    if config_key == "testing":
        testing_settings = TestingSettings()
        return testing_settings.model_dump(by_alias=True)
    if config_key == "local":
        settings = Settings()  # type: ignore[call-arg]
        return settings.model_dump(by_alias=True)

    raise KeyError(config_key)


def get_log_settings() -> LogSettings:
    return _log_settings
