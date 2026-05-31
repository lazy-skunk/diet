from sqlalchemy.exc import SQLAlchemyError

from diet.extensions import sql_alchemy
from diet.utils.custom_logger import get_logger

_logger = get_logger()


def commit() -> None:
    _logger.info("Start")

    try:
        sql_alchemy.session.commit()
    except SQLAlchemyError as e:
        sql_alchemy.session.rollback()
        _logger.error(e, exc_info=True)
        raise

    _logger.info("End")
