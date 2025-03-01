from flask_login import UserMixin
from sqlalchemy.orm import validates

from apps.extensions import sql_alchemy
from apps.utils.custom_logger import CustomLogger
from apps.utils.validation_util import ValidationUtil

_logger = CustomLogger.get_logger()

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
        _logger.debug(f"Start: {key}={username}")

        ValidationUtil.validate_not_none(key, username)
        username = username.strip()
        ValidationUtil.validate_not_empty(key, username)

        _logger.debug(f"End: {key}={username}")
        return username

    @validates("email")
    def validate_email(self, key: str, email: str) -> str:
        _logger.debug(f"Start: {key}={email}")

        ValidationUtil.validate_not_none(key, email)
        email = email.strip().lower()
        ValidationUtil.validate_not_empty(key, email)
        ValidationUtil.validate_by_regexp(key, email, _EMAIL_REGEXP)
        ValidationUtil.validate_by_max_length(key, email, _MAX_EMAIL_LENGTH)
        ValidationUtil.validate_unique(User, key, email)

        _logger.debug(f"End: {key}={email}")
        return email
