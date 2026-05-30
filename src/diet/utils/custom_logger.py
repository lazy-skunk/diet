import logging
import os
from logging import Formatter, Logger, StreamHandler
from logging.handlers import RotatingFileHandler

from diet.config import get_log_settings

_log_settings = get_log_settings()

_STREAM_HANDLER_NAME = "diet_stream_handler"
_FILE_HANDLER_NAME = "diet_file_handler"


def get_logger() -> Logger:
    logger = logging.getLogger(__name__)

    if _has_configured_handlers(logger):
        return logger

    log_level = _log_settings.log_level
    logger.setLevel(log_level)

    log_path = _log_settings.log_path
    _ensure_log_directory(log_path)

    formatter = Formatter(
        "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    _add_stream_handler(logger, log_level, formatter)
    _add_rotating_file_handler(logger, log_level, log_path, formatter)

    return logger


def _has_configured_handlers(logger: Logger) -> bool:
    handler_names = {handler.get_name() for handler in logger.handlers}
    return {_STREAM_HANDLER_NAME, _FILE_HANDLER_NAME}.issubset(handler_names)


def _ensure_log_directory(path: str) -> None:
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)


def _add_stream_handler(
    logger: Logger, log_level: str | int, formatter: Formatter
) -> None:
    stream_handler = StreamHandler()
    stream_handler.set_name(_STREAM_HANDLER_NAME)
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)


def _add_rotating_file_handler(
    logger: Logger, log_level: str | int, log_path: str, formatter: Formatter
) -> None:
    rotating_file_handler = RotatingFileHandler(
        log_path,
        maxBytes=_log_settings.log_size,
        backupCount=_log_settings.log_backup,
    )
    rotating_file_handler.set_name(_FILE_HANDLER_NAME)
    rotating_file_handler.setLevel(log_level)
    rotating_file_handler.setFormatter(formatter)

    logger.addHandler(rotating_file_handler)
