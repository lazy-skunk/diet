import datetime

from diet.body_composition.models import BodyComposition
from diet.extensions import sql_alchemy
from diet.utils.custom_logger import get_logger

_logger = get_logger()


def get_body_compositions(user_id: int) -> list[BodyComposition]:
    _logger.info(f"Start: {user_id=}")

    records = (
        BodyComposition.query.filter_by(user_id=user_id)
        .order_by(BodyComposition.date.asc())
        .all()
    )
    if not records:
        _logger.info(f"End: No records found - {user_id=}")
        return []

    _logger.info(f"End: Records found - {user_id=}")
    return records


def get_latest_by_user(user_id: int) -> BodyComposition | None:
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


def get_by_user_and_date(
    user_id: int, date: datetime.date
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


def upsert(
    user_id: int, date: datetime.date, weight: float, body_fat: float | None
) -> None:
    _logger.info(f"Start: {user_id=}, {date=}, {weight=}, {body_fat=}")

    record = get_by_user_and_date(user_id, date)
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

    _logger.info(
        f"End: {record.user_id=}, {record.date=}"
        f", {record.weight=}, {record.body_fat=}"
    )
