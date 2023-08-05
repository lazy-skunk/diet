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
    date = DateField("日付", validators=[DataRequired()], default=date.today)
    weight = FloatField(
        "体重（kg）", validators=[DataRequired(), NumberRange(min=0.1, max=999.9)]
    )
    body_fat = FloatField("体脂肪率（%）", validators=[NumberRange(min=0, max=100)])
    submit = SubmitField("記録")


class SignupForm(FlaskForm):
    username = StringField("ユーザー名", validators=[DataRequired()])
    email = StringField("Eメール", validators=[DataRequired(), Email()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    confirm_password = PasswordField(
        "パスワード（確認用）",
        validators=[DataRequired(), EqualTo("password", message="パスワードが一致しません")],
    )
    submit = SubmitField("登録")


class SigninForm(FlaskForm):
    username = StringField("ユーザー名", validators=[DataRequired()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    submit = SubmitField("ログイン")
