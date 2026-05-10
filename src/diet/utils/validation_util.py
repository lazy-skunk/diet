import datetime
import re
from datetime import date
from typing import NoReturn

from diet.utils.custom_logger import get_logger

_logger = get_logger()

_VALIDATION_FAILED_MSG = "Validation failed: {key} - {reason}"


def validate_not_none(key: str, value: object) -> None:
    if value is None:
        _raise_validation_error(key, "Cannot be None", TypeError)


def validate_not_empty(key: str, value: str) -> None:
    if not value.strip():
        _raise_validation_error(
            key, "Cannot be empty or whitespace only", ValueError
        )


def validate_by_regexp(key: str, value: str, pattern: str) -> None:
    if not re.fullmatch(pattern, value):
        _raise_validation_error(key, "Invalid format", ValueError)


def validate_by_max_length(key: str, value: str, max_length: int) -> None:
    if len(value) > max_length:
        reason = f"Exceeds max length ({max_length} characters)"
        _raise_validation_error(key, reason, ValueError)


def validate_date(key: str, value: datetime.date) -> None:
    if value > date.today():
        reason = f"{value} is in the future and cannot be used"
        _raise_validation_error(key, reason, ValueError)


def validate_number_range(
    key: str, value: float, min_value: float, max_value: float
) -> None:
    if not (min_value <= value <= max_value):
        reason = f"Must be between {min_value} and {max_value}"
        _raise_validation_error(key, reason, ValueError)


def _raise_validation_error(
    key: str, reason: str, error_type: type[Exception]
) -> NoReturn:
    message = _VALIDATION_FAILED_MSG.format(key=key, reason=reason)
    _logger.warning(message)
    raise error_type(message)
