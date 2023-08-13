from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    FloatField,
    PasswordField,
    StringField,
    SubmitField,
    validators,
)
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange


class LogWeightForm(FlaskForm):
    """
    体重と体脂肪率の記録フォーム。

    Fields:
    - date: 日付を入力するフィールド。デフォルトは今日の日付。
    - weight: 体重を入力するフィールド。0.1〜999.9の範囲。
    - body_fat: 体脂肪率を入力するフィールド。0〜99.9%の範囲。
    - submit: フォームを送信するボタン。
    """

    date = DateField("日付", validators=[DataRequired()], default=date.today)
    weight = FloatField(
        "体重(kg)", validators=[DataRequired(), NumberRange(min=0.1, max=999.9)]
    )
    body_fat = FloatField("体脂肪率(%)", validators=[NumberRange(min=0, max=99.9)])
    submit = SubmitField("記録")


class SignupForm(FlaskForm):
    """
    新規ユーザー登録フォーム。

    Fields:
    - username: ユーザー名を入力するフィールド。
    - email: Eメールアドレスを入力するフィールド。正しいEメール形式である必要がある。
    - password: パスワードを入力するフィールド。
    - confirm_password: 確認用のパスワードを入力するフィールド。passwordフィールドと一致している必要がある。
    - submit: フォームを送信するボタン。
    """

    username = StringField("ユーザー名", validators=[DataRequired()])
    email = StringField("Eメール", validators=[DataRequired(), Email()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    confirm_password = PasswordField(
        "パスワード(確認用)",
        validators=[DataRequired(), EqualTo("password", message="パスワードが一致しません。")],
    )
    submit = SubmitField("登録")


class SigninForm(FlaskForm):
    """
    ログインフォーム。

    Fields:
    - username: ユーザー名を入力するフィールド。
    - password: パスワードを入力するフィールド。
    - submit: フォームを送信するボタン。
    """

    username = StringField("ユーザー名", validators=[DataRequired()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    submit = SubmitField("ログイン")
