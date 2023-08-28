from datetime import date

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    """
    Userモデル: アプリケーションのユーザー情報を表現する。

    Attributes:
    - id: ユーザーの一意のID。
    - username: ユーザー名。
    - email: ユーザーのEメールアドレス。一意でなければならない。
    - password_hash: ハッシュ化されたパスワード。
    - logs: ユーザーに関連する体組成のログ。

    Methods:
    - check_password: 与えられたパスワードがハッシュ化されたパスワードと一致するかどうかをチェックする。
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    logs = db.relationship("BodyComposition", backref="user", lazy=True)

    def __init__(self, username, email, password):
        """
        Userインスタンスを初期化する。

        Parameters:
        - username (str): ユーザー名。
        - email (str): ユーザーのEメールアドレス。
        - password (str): ユーザーの生のパスワード。この関数内でハッシュ化される。
        """
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        パスワードがハッシュ化されたパスワードと一致するかを確認する。

        Parameters:
        - password (str): 検証するパスワード。

        Returns:
        - bool: パスワードが一致する場合はTrue、それ以外の場合はFalse。
        """
        return check_password_hash(self.password_hash, password)

    @validates("username")
    def validate_username(self, key, username):
        """
        ユーザー名のバリデーション。

        Parameters:
        - key: この場合は 'username'。
        - username (str): 検証するユーザー名。

        Returns:
        - str: バリデーションが成功した場合のユーザー名。

        Raises:
        - AssertionError: ユーザー名が無効な場合。
        """
        if not username:
            raise AssertionError("ユーザー名は必須です。")
        return username

    @validates("email")
    def validate_email(self, key, email):
        """
        Eメールのバリデーション。

        Parameters:
        - key: この場合は 'email'。
        - email (str): 検証するEメールアドレス。

        Returns:
        - str: バリデーションが成功した場合のEメールアドレス。

        Raises:
        - AssertionError: Eメールアドレスが無効な場合。
        """
        if not email:
            raise AssertionError("Eメールは必須です。")
        if "@" not in email:
            raise AssertionError("有効なEメールアドレスを入力してください。")
        return email


class BodyComposition(db.Model):
    """
    BodyCompositionモデル: ユーザーの体組成情報を表現する。

    Attributes:
    - id: ログの一意のID。
    - date: 体組成情報の日付。
    - weight: 体重。
    - body_fat: 体脂肪率。
    - user_id: このログに関連するユーザーのID。
    """

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    body_fat = db.Column(db.Float, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, date, weight, body_fat=None, user_id=None):
        """
        BodyCompositionインスタンスを初期化する。

        Parameters:
        - date (date): 体組成情報の日付。
        - weight (float): 体重。
        - body_fat (float, optional): 体脂肪率。デフォルトはNone。
        - user_id (int, optional): このログに関連するユーザーのID。デフォルトはNone。
        """
        self.date = date
        self.weight = weight
        self.body_fat = body_fat
        self.user_id = user_id

    @validates("date")
    def validate_date(self, key, input_date):
        """
        日付のバリデーション。未来の日付は許可しない。

        Parameters:
        - key: この場合は 'date'。
        - input_date (date): 検証する日付。

        Returns:
        - date: バリデーションが成功した場合の日付。

        Raises:
        - AssertionError: 入力された日付が未来の場合。
        """
        if input_date > date.today():
            raise AssertionError("未来の日付は許可されていません。")
        return input_date

    @validates("weight")
    def validate_weight(self, key, weight):
        """
        体重のバリデーション。

        Parameters:
        - key: この場合は 'weight'。
        - weight (float): 検証する体重。

        Returns:
        - float: バリデーションが成功した場合の体重。

        Raises:
        - AssertionError: 体重が無効な範囲の場合。
        """
        if weight < 0.1 or weight > 999.9:
            raise AssertionError("体重は0.1〜999.9の範囲内である必要があります。")
        return weight

    @validates("body_fat")
    def validate_body_fat(self, key, body_fat):
        """
        体脂肪率のバリデーション。

        Parameters:
        - key: この場合は 'body_fat'。
        - body_fat (float): 検証する体脂肪率。

        Returns:
        - float: バリデーションが成功した場合の体脂肪率。

        Raises:
        - AssertionError: 体脂肪率が無効な範囲の場合。
        """
        if body_fat is not None and (body_fat < 0.1 or body_fat > 99.9):
            raise AssertionError("体脂肪率は0.1〜99.9%の範囲内である必要があります。")
        return body_fat
