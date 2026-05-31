from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from diet.auth.models import User
from diet.auth.repository import create, find_by_email
from diet.utils.custom_logger import get_logger
from diet.utils.transaction import commit

_logger = get_logger()


def register_user(username: str, email: str, password: str) -> User:
    _logger.info(f"Start: {username=}, {email=}")

    normalized_email = email.strip().lower()
    if find_by_email(normalized_email):
        _logger.info(f"End: failed (Email already registered) - {email=}")
        raise ValueError("Email is already registered.")

    new_user = User(username=username, email=normalized_email)
    new_user.password_hash = generate_password_hash(password)

    try:
        create(new_user)
        commit()
    except IntegrityError as e:
        raise ValueError("Email is already registered.") from e

    _logger.info(
        f"End: {new_user.id=} {new_user.username=}, {new_user.email=}"
    )
    return new_user


def authenticate_user(email: str, password: str) -> User | None:
    _logger.info(f"Start: {email=}")

    normalized_email = email.strip().lower()
    user: User | None = find_by_email(normalized_email)

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


def update_password(
    user: User, current_password: str, new_password: str
) -> None:
    _logger.info(f"Start: {user.id=}, {user.username=}, {user.email=}")

    if not check_password_hash(user.password_hash, current_password):
        _logger.info(
            f"End: failed (Invalid credentials) - {user.id=}"
            f", {user.username=}, {user.email=}"
        )
        raise ValueError("Invalid current password.")

    user.password_hash = generate_password_hash(new_password)
    commit()
    _logger.info(f"End: {user.id=} {user.username=}, {user.email=}")


def update_username(user: User, new_username: str) -> None:
    _logger.info(f"Start: {user.id=}, {user.username=}, {user.email=}")

    normalized_username = new_username.strip()
    if user.username == normalized_username:
        _logger.info(f"End: unchanged - {user.id=}, {user.username=}")
        return

    user.username = normalized_username
    commit()
    _logger.info(f"End: {user.id=} {user.username=}, {user.email=}")
