from werkzeug.security import check_password_hash, generate_password_hash

from diet.auth.models import User
from diet.auth.repository import create, find_by_email, update
from diet.utils.custom_logger import get_logger

_logger = get_logger()


def register_user(username: str, email: str, password: str) -> User:
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
    update(user)
    _logger.info(f"End: {user.id=} {user.username=}, {user.email=}")


def update_username(user: User, new_username: str) -> None:
    _logger.info(f"Start: {user.id=}, {user.username=}, {user.email=}")

    normalized_username = new_username.strip()
    if user.username == normalized_username:
        _logger.info(f"End: unchanged - {user.id=}, {user.username=}")
        return

    user.username = normalized_username
    update(user)
    _logger.info(f"End: {user.id=} {user.username=}, {user.email=}")
