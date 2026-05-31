import datetime

from sqlalchemy.orm import validates

from diet.body_composition.constants import (
    MAX_BODY_FAT,
    MAX_WEIGHT,
    MIN_BODY_FAT,
    MIN_WEIGHT,
)
from diet.extensions import sql_alchemy
from diet.utils.custom_logger import get_logger
from diet.utils.validation_util import (
    validate_date,
    validate_not_none,
    validate_number_range,
)

_logger = get_logger()


class BodyComposition(sql_alchemy.Model):  # type: ignore
    __table_args__ = (
        sql_alchemy.UniqueConstraint(
            "user_id", "date", name="uq_body_composition_user_date"
        ),
    )

    id = sql_alchemy.Column(sql_alchemy.Integer, primary_key=True)
    user_id = sql_alchemy.Column(
        sql_alchemy.Integer, sql_alchemy.ForeignKey("user.id"), nullable=False
    )
    date = sql_alchemy.Column(sql_alchemy.Date, nullable=False)
    weight = sql_alchemy.Column(sql_alchemy.Float, nullable=False)
    body_fat = sql_alchemy.Column(sql_alchemy.Float, nullable=True)

    def __init__(
        self,
        user_id: int,
        date: datetime.date,
        weight: float,
        body_fat: float | None = None,
    ) -> None:
        self.user_id = user_id
        self.date = date
        self.weight = weight
        self.body_fat = body_fat

    @validates("date")
    def validate_date(
        self, key: str, input_date: datetime.date
    ) -> datetime.date:
        _logger.debug(f"Start: {key=}, {input_date=}")

        validate_not_none(key, input_date)
        validate_date(key, input_date)

        _logger.debug(f"End: {key=}, {input_date=}")
        return input_date

    @validates("weight")
    def validate_weight(self, key: str, weight: float) -> float:
        _logger.debug(f"Start: {key=}, {weight=}")

        validate_not_none(key, weight)
        validate_number_range(key, weight, MIN_WEIGHT, MAX_WEIGHT)

        _logger.debug(f"End: {key=}, {weight=}")
        return weight

    @validates("body_fat")
    def validate_body_fat(
        self, key: str, body_fat: float | None
    ) -> float | None:
        _logger.debug(f"Start: {key=}, {body_fat=}")

        if body_fat is not None:
            validate_number_range(key, body_fat, MIN_BODY_FAT, MAX_BODY_FAT)

        _logger.debug(f"End: {key=}, {body_fat=}")
        return body_fat
