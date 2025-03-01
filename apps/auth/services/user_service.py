from werkzeug.security import check_password_hash, generate_password_hash

from apps.auth.models import User
from apps.auth.repositories.user_repository import UserRepository
from apps.utils.custom_logger import CustomLogger

_logger = CustomLogger.get_logger()


class UserService:
    @staticmethod
    def create(username: str, email: str, password: str) -> User:
        _logger.info(f"Start: {username=}, {email=}")

        new_user = User(username=username, email=email)
        new_user.password_hash = generate_password_hash(password)

        UserRepository.create(new_user)

        _logger.info(
            f"End: {new_user.id=} {new_user.username=}, {new_user.email=}"
        )
        return new_user

    @staticmethod
    def authenticate(email: str, password: str) -> User | None:
        _logger.info(f"Start: {email=}")

        user: User | None = UserRepository.find_by_email(email)

        if not user:
            _logger.info(f"End: failed (User not found) - {email=}")
            return None

        if check_password_hash(user.password_hash, password):
            _logger.info(f"End: succeeded - {email=}")
            return user
        else:
            _logger.info(f"End: failed (Invalid credentials) - {email=}")
            return None
