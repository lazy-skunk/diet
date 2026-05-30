from diet.auth.models import User
from diet.extensions import sql_alchemy
from diet.utils.custom_logger import get_logger

_logger = get_logger()


def create(user: User) -> None:
    _logger.info(f"Start: {user.id=}, {user.username=}, {user.email=}")

    sql_alchemy.session.add(user)

    _logger.info(f"End: {user.id=}, {user.username=}, {user.email=}")


def update(user: User) -> None:
    _logger.info(f"Start: {user.id=}, {user.username=}, {user.email=}")
    _logger.info(f"End: {user.id=}, {user.username=}, {user.email=}")


def find_by_email(email: str) -> User | None:
    _logger.info(f"Start: {email=}")

    user: User | None = User.query.filter_by(email=email).first()

    if not user:
        _logger.info(f"End: User not found - {email=}")
        return None

    _logger.info(
        f"End: User found - {user.id=}, {user.username=}, {user.email=}"
    )
    return user


def find_by_id(id: str) -> User:
    _logger.info(f"Start: {id=}")

    user: User = User.query.filter_by(id=id).first()

    _logger.info(f"End: {user.id=}, {user.username=}, {user.email=}")
    return user
