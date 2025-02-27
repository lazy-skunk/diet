import datetime
from datetime import date

from sqlalchemy.orm import validates

from apps.extensions import sql_alchemy


class BodyComposition(sql_alchemy.Model):
    id = sql_alchemy.Column(sql_alchemy.Integer, primary_key=True)
    date = sql_alchemy.Column(sql_alchemy.Date, nullable=False)
    weight = sql_alchemy.Column(sql_alchemy.Float, nullable=False)
    body_fat = sql_alchemy.Column(sql_alchemy.Float, nullable=True)

    user_id = sql_alchemy.Column(
        sql_alchemy.Integer, sql_alchemy.ForeignKey("user.id"), nullable=False
    )

    def __init__(
        self,
        date: datetime.date,
        weight: float,
        body_fat: float | None = None,
        user_id: str | None = None,
    ) -> None:
        self.date = date
        self.weight = weight
        self.body_fat = body_fat
        self.user_id = user_id

    @validates("date")
    def validate_date(
        self, _: str, input_date: datetime.date
    ) -> datetime.date:
        if input_date > date.today():
            raise AssertionError("今日以前の日付を選択してください。")
        return input_date

    @validates("weight")
    def validate_weight(self, _: str, weight: float) -> float:
        if weight < 0.1 or weight > 999.9:
            raise AssertionError(
                "体重は 0.1 から 999.9 の間で入力してください。"
            )
        return weight

    @validates("body_fat")
    def validate_body_fat(self, _: str, body_fat: float) -> float:
        if body_fat is not None and (body_fat < 0.1 or body_fat > 99.9):
            raise AssertionError(
                "体脂肪率は 0 から 99.9 の間で入力してください。"
            )
        return body_fat
