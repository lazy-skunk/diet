from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
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
    body_fat = db.Column(db.Float)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, date, weight, body_fat=None, user_id=user_id):
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
