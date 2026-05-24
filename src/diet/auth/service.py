from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from diet.auth.models import User
from diet.auth.repository import create, find_by_email, update
from diet.utils.custom_logger import get_logger

_logger = get_logger()


def create_user(username: str, email: str, password: str) -> User:
    _logger.info(f"Start: {username=}, {email=}")

    new_user = User(username=username, email=email)
    new_user.password_hash = generate_password_hash(password)

    create(new_user)

    _logger.info(
        f"End: {new_user.id=} {new_user.username=}, {new_user.email=}"
    )
    return new_user


def authenticate_user(email: str, password: str) -> User | None:
    _logger.info(f"Start: {email=}")

    user: User | None = find_by_email(email)

    if not user:
        _logger.info(f"End: failed (User not found) - {email=}")
        return None

    if check_password_hash(user.password_hash, password):
        _logger.info(
            f"End: succeeded - {user.id=}, {user.username=}, {user.email=}"
        )
        return user

    _logger.info(
        f"End: failed (Invalid credentials) - {user.id=}"
        f", {user.username=}, {user.email=}"
    )
    return None


def change_password(
    user: User, current_password: str, new_password: str
) -> bool:
    _logger.info(f"Start: {user.id=}, {user.username=}, {user.email=}")

    if not check_password_hash(user.password_hash, current_password):
        _logger.info(
            f"End: failed (Invalid credentials) - {user.id=}"
            f", {user.username=}, {user.email=}"
        )
        return False

    try:
        user.password_hash = generate_password_hash(new_password)
        update(user)
        _logger.info(f"End: {user.id=} {user.username=}, {user.email=}")
        return True
    except SQLAlchemyError as e:
        _logger.error(e, exc_info=True)
        return False


def change_username(user: User, new_username: str) -> bool:
    _logger.info(f"Start: {user.id=}, {user.username=}, {user.email=}")

    try:
        user.username = new_username
        update(user)
        _logger.info(f"End: {user.id=} {user.username=}, {user.email=}")
        return True
    except SQLAlchemyError as e:
        _logger.error(e, exc_info=True)
        return False

    # @staticmethod
    # def validate_unique(model: Any, key: str, value: str) -> None:
    #     exists = model.query.filter(getattr(model, key) == value).first()
    #     if exists:
    #         reason = f"{value} cannot be used"
    #         message = _VALIDATION_FAILED_MSG.format(key=key, reason=reason)
    #         _logger.warning(message)
    #         raise ValueError(message)
