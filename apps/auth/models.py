from typing import Self

from flask_login import UserMixin
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import validates
from werkzeug.security import check_password_hash, generate_password_hash

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

    @classmethod
    def authenticate(cls, email: str, password: str) -> Self | None:
        _logger.info("Starting user authentication.")
        _logger.debug(f"Authenticating user: email={email}")

        user: Self = cls.query.filter_by(email=email).first()

        if user and user._check_password(password):
            _logger.info("User authentication completed successfully.")
            _logger.debug(
                f"Authenticated user: id={user.id}, email={user.email}"
            )
            return user

        _logger.warning("User authentication failed. Invalid credentials.")
        return None

    @classmethod
    def create(cls, username: str, email: str, password: str) -> Self:
        _logger.info("Starting user creation.")
        _logger.debug(f"Creating user: username={username}, email={email}")

        new_user = cls(username, email)
        new_user._set_password(password)

        try:
            sql_alchemy.session.add(new_user)
            sql_alchemy.session.commit()
            _logger.info("User creation completed successfully.")
            _logger.debug(
                f"Created user: id={new_user.id},"
                f" username={new_user.username}, email={new_user.email}"
            )
        except SQLAlchemyError:
            sql_alchemy.session.rollback()
            _logger.error(
                "User creation failed due to database error.", exc_info=True
            )
            raise

        return new_user

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

    def _set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def _check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
