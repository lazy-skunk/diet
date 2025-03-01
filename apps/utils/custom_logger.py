import logging
import os
from logging import Formatter, Logger, StreamHandler
from logging.handlers import RotatingFileHandler

from apps.utils.directory_util import DirectoryUtil

_DEFAULT_LOG_LEVEL = logging.DEBUG
_DEFAULT_LOG_PATH = "log/app.log"
_DEFAULT_LOG_SIZE = 1024 * 1024 * 10
_DEFAULT_LOG_BACKUP = 3


class CustomLogger:
    _logger: Logger | None = None

    @classmethod
    def get_logger(cls) -> Logger:
        cls._initialize()

        if cls._logger is None:  # pragma: no cover
            raise RuntimeError("Logger has not been initialized.")

        return cls._logger

    @classmethod
    def _initialize(cls) -> None:
        if cls._logger is None:
            cls._logger = logging.getLogger(__name__)

            log_level = os.getenv("LOG_LEVEL", _DEFAULT_LOG_LEVEL)
            cls._logger.setLevel(log_level)

            log_path = os.getenv("LOG_PATH", _DEFAULT_LOG_PATH)
            DirectoryUtil.ensure_directory(log_path)

            formatter = Formatter(
                "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s",  # noqa E501
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            cls._add_stream_handler(log_level, formatter)
            cls._add_rotating_file_handler(log_level, log_path, formatter)

    @classmethod
    def _add_stream_handler(
        cls, log_level: str | int, formatter: Formatter
    ) -> None:
        if cls._logger is None:  # pragma: no cover
            raise RuntimeError("Logger has not been initialized.")

        stream_handler = StreamHandler()
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(formatter)

        cls._logger.addHandler(stream_handler)

    @classmethod
    def _add_rotating_file_handler(
        cls, log_level: str | int, log_path: str, formatter: Formatter
    ) -> None:
        if cls._logger is None:  # pragma: no cover
            raise RuntimeError("Logger has not been initialized.")

        log_size = int(os.getenv("LOG_SIZE", _DEFAULT_LOG_SIZE))
        log_backup = int(os.getenv("LOG_BACKUP", _DEFAULT_LOG_BACKUP))

        rotating_file_handler = RotatingFileHandler(
            log_path, maxBytes=log_size, backupCount=log_backup
        )
        rotating_file_handler.setLevel(log_level)
        rotating_file_handler.setFormatter(formatter)

        cls._logger.addHandler(rotating_file_handler)
