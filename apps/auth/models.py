from flask_login import UserMixin
from sqlalchemy.orm import validates

from apps.extensions import sql_alchemy
from apps.utils.singleton_logger import SingletonLogger
from apps.utils.validation_helper import ValidationHelper

_logger = SingletonLogger.get_logger()

_EMAIL_REGEXP = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
_MAX_EMAIL_LENGTH = 254


class User(sql_alchemy.Model, UserMixin):  # type: ignore
    id = sql_alchemy.Column(sql_alchemy.Integer, primary_key=True)
    username = sql_alchemy.Column(sql_alchemy.String(80), nullable=False)
    email = sql_alchemy.Column(
        sql_alchemy.String(120), unique=True, nullable=False
    )
    password_hash = sql_alchemy.Column(sql_alchemy.String(128), nullable=False)

    def __init__(self, username: str, email: str) -> None:
        self.username = username
        self.email = email

    @validates("username")
    def validate_username(self, key: str, username: str) -> str:
        _logger.debug(f"Validating {key}: {key}={username}")

        ValidationHelper.validate_not_none(key, username)
        username = username.strip()
        ValidationHelper.validate_not_empty(key, username)

        _logger.debug(f"Validation passed: {key}={username}")
        return username

    @validates("email")
    def validate_email(self, key: str, email: str) -> str:
        _logger.debug(f"Validating {key}: {key}={email}")

        ValidationHelper.validate_not_none(key, email)
        email = email.strip().lower()
        ValidationHelper.validate_not_empty(key, email)
        ValidationHelper.validate_by_regexp(key, email, _EMAIL_REGEXP)
        ValidationHelper.validate_by_max_length(key, email, _MAX_EMAIL_LENGTH)
        ValidationHelper.validate_unique(User, key, email)

        _logger.debug(f"Validation passed: {key}={email}")
        return email
