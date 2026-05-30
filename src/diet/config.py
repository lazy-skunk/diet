from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str
    wtf_csrf_secret_key: str
    database_url: str = f"sqlite:///{_BASE_DIR / 'local.sqlite'}"


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


_settings = Settings()  # type: ignore[call-arg]
_log_settings = LogSettings()


class BaseConfig:
    SECRET_KEY = _settings.secret_key
    WTF_CSRF_SECRET_KEY = _settings.wtf_csrf_secret_key
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = _settings.database_url
    SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    SECRET_KEY = "testing-secret-key"
    WTF_CSRF_SECRET_KEY = "testing-csrf-secret-key"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{_BASE_DIR / 'testing.sqlite'}"
    WTF_CSRF_ENABLED = False


_CONFIG = {
    "testing": TestingConfig,
    "local": LocalConfig,
}


def get_config(config_key: str) -> type[BaseConfig]:
    return _CONFIG[config_key]


def get_log_settings() -> LogSettings:
    return _log_settings
