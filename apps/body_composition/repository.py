import datetime

from sqlalchemy.exc import SQLAlchemyError

from apps.body_composition.models import BodyComposition
from apps.extensions import sql_alchemy
from apps.utils.custom_logger import CustomLogger

_logger = CustomLogger.get_logger()


class BodyCompositionRepository:
    @staticmethod
    def get_body_compositions(user_id: str) -> list[BodyComposition] | None:
        _logger.info(f"Start: {user_id=}")

        records = (
            BodyComposition.query.filter_by(user_id=user_id)
            .order_by(BodyComposition.date.asc())
            .all()
        )
        if not records:
            _logger.info(f"End: No records found - {user_id=}")
            return None

        _logger.info(f"End: Records found - {user_id=}")
        return records

    @staticmethod
    def get_latest_by_user(user_id: str) -> BodyComposition | None:
        _logger.info(f"Start: {user_id=}")

        record = (
            BodyComposition.query.filter_by(user_id=user_id)
            .order_by(BodyComposition.date.desc())
            .first()
        )
        if not record:
            _logger.info(f"End: No record found - {user_id=}")
            return None

        _logger.info(f"End: Record found - {user_id=}")
        return record

    @staticmethod
    def get_by_user_and_date(
        user_id: str, date: datetime.date
    ) -> BodyComposition | None:
        _logger.info(f"Start: {user_id=}, {date=}")

        record = BodyComposition.query.filter_by(
            user_id=user_id, date=date
        ).first()
        if not record:
            _logger.info(f"End: No record found - {user_id=}, {date=}")
            return None

        _logger.info(f"End: Record found - {user_id=}, {date=}")
        return record

    @staticmethod
    def upsert(
        user_id: str, date: datetime.date, weight: float, body_fat: float
    ) -> None:
        _logger.info(f"Start: {user_id=}, {date=}, {weight=}, {body_fat=}")

        record: BodyComposition | None = (
            BodyCompositionRepository.get_by_user_and_date(user_id, date)
        )
        if record:
            if record.weight != weight or record.body_fat != body_fat:
                _logger.info(
                    f"Progress: Before commit - {record.weight=}"
                    f", {weight=}, {record.body_fat=}, {body_fat=}"
                )
                record.weight = weight
                record.body_fat = body_fat
            else:
                _logger.info(
                    f"End: No change detected - {record.weight=}"
                    f", {weight=}, {record.body_fat=}, {body_fat=}"
                )
                return
        else:
            record = BodyComposition(
                date=date, weight=weight, body_fat=body_fat, user_id=user_id
            )
            sql_alchemy.session.add(record)

        try:
            sql_alchemy.session.commit()
        except SQLAlchemyError as e:
            sql_alchemy.session.rollback()
            _logger.error(e, exc_info=True)
            raise

        _logger.info(
            f"End: {record.user_id=}, {record.date=}"
            f", {record.weight=}, {record.body_fat=}"
        )
