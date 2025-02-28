from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from apps.auth.models import User
from apps.extensions import sql_alchemy
from apps.utils.singleton_logger import SingletonLogger

_logger = SingletonLogger.get_logger()


class UserService:
    @staticmethod
    def create(username: str, email: str, password: str) -> User:
        _logger.info("Starting user creation.")

        new_user = User(username=username, email=email)
        new_user.password_hash = generate_password_hash(password)

        try:
            sql_alchemy.session.add(new_user)
            sql_alchemy.session.commit()
            _logger.info("User creation completed successfully.")
            return new_user
        except SQLAlchemyError:
            sql_alchemy.session.rollback()
            _logger.error(
                "User creation failed due to database error.", exc_info=True
            )
            raise

    @staticmethod
    def authenticate(email: str, password: str) -> User | None:
        _logger.info("Starting user authentication.")

        user: User = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            _logger.info("User authentication completed successfully.")
            return user

        _logger.info("User authentication failed. Invalid credentials.")
        return None
