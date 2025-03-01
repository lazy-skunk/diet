import datetime
import re
from datetime import date
from typing import Any

from apps.utils.singleton_logger import SingletonLogger

_logger = SingletonLogger.get_logger()

_VALIDATION_FAILED_MSG = "Validation failed: {key} - {reason}"


class ValidationUtil:
    @staticmethod
    def validate_not_none(key: str, value: object) -> None:
        if value is None:
            reason = "Cannot be None."
            message = _VALIDATION_FAILED_MSG.format(key=key, reason=reason)
            _logger.warning(message)
            raise TypeError(message)

    @staticmethod
    def validate_not_empty(key: str, value: str) -> None:
        if not value.strip():
            reason = "Cannot be empty or whitespace only."
            message = _VALIDATION_FAILED_MSG.format(key=key, reason=reason)
            _logger.warning(message)
            raise ValueError(message)

    @staticmethod
    def validate_by_regexp(key: str, value: str, pattern: str) -> None:
        if not re.fullmatch(pattern, value):
            reason = "Invalid format."
            message = _VALIDATION_FAILED_MSG.format(key=key, reason=reason)
            _logger.warning(message)
            raise ValueError(message)

    @staticmethod
    def validate_by_max_length(key: str, value: str, max_length: int) -> None:
        if len(value) > max_length:
            reason = f"Exceeds max length ({max_length} characters)."
            message = _VALIDATION_FAILED_MSG.format(key=key, reason=reason)
            _logger.warning(message)
            raise ValueError(message)

    @staticmethod
    def validate_unique(model: Any, key: str, value: str) -> None:
        exists = model.query.filter(getattr(model, key) == value).first()
        if exists:
            reason = f"{value} cannot be used."
            message = _VALIDATION_FAILED_MSG.format(key=key, reason=reason)
            _logger.warning(message)
            raise ValueError(message)

    @staticmethod
    def validate_date(key: str, value: datetime.date) -> None:
        if value > date.today():
            reason = f"{value} is in the future and cannot be used."
            message = _VALIDATION_FAILED_MSG.format(key=key, reason=reason)
            _logger.warning(message)
            raise ValueError(message)

    @staticmethod
    def validate_number_range(
        key: str, value: float, min_value: float, max_value: float
    ) -> None:
        if not (min_value <= value <= max_value):
            reason = f"Must be between {min_value} and {max_value}."
            message = _VALIDATION_FAILED_MSG.format(key=key, reason=reason)
            _logger.warning(message)
            raise ValueError(message)
