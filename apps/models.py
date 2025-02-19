import datetime
from datetime import date

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    logs = db.relationship("BodyComposition", backref="user", lazy=True)

    def __init__(self, username: str, email: str, password: str) -> None:
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @validates("username")
    def validate_username(self, _: str, username: str) -> str:
        if not username:
            raise AssertionError("ユーザー名を入力してください。")
        return username

    @validates("email")
    def validate_email(self, _: str, email: str) -> str:
        if not email:
            raise AssertionError("Eメールアドレスを入力してください。")
        if "@" not in email:
            raise AssertionError("有効なEメールアドレスを入力してください。")
        return email


class BodyComposition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    body_fat = db.Column(db.Float, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

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
