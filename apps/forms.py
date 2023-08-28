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
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    NumberRange,
    Optional,
    ValidationError,
)


class BaseLogWeightForm(FlaskForm):
    """
    体重と体脂肪率の記録のためのベースフォーム。

    Fields:
    - date: 日付を入力するフィールド。デフォルトは今日の日付。未来の日付は許可されていない。
    - weight: 体重を入力するフィールド。0.1〜999.9の範囲。
    - body_fat: 体脂肪率を入力するフィールド。0〜99.9%の範囲。
    """

    def validate_not_future_date(form, field):
        """
        日付フィールドが未来の日付でないことを確認するカスタムバリデータ。

        Parameters:
        - form: バリデーションを行っているフォームのインスタンス。
        - field: バリデーションを行っているフィールドのインスタンス。

        Raises:
        - ValidationError: フィールドのデータが今日の日付よりも未来の場合。
        """
        if field.data > date.today():
            raise ValidationError("未来の日付は許可されていません。")

    today = date.today().isoformat()

    date = DateField(
        "日付",
        validators=[DataRequired(), validate_not_future_date],
        default=date.today,
        render_kw={"max": today},
    )
    weight = FloatField(
        "体重 (kg)",
        validators=[
            DataRequired(message="体重 (kg) には正の整数、または正の浮動小数点数を入力してください。"),
            NumberRange(min=0.1, max=999.9),
        ],
    )
    body_fat = FloatField(
        "体脂肪率 (%)", validators=[Optional(), NumberRange(min=0.1, max=99.9)]
    )


class LogWeightForm(BaseLogWeightForm):
    """
    体重と体脂肪率の記録フォーム。

    Fields:
    Inherits fields from BaseLogWeightForm.
    - submit: フォームを送信するボタン。
    """

    submit = SubmitField("記録")


class SignupForm(BaseLogWeightForm):
    """
    新規ユーザー登録フォーム。

    Fields:
    Inherits fields from BaseLogWeightForm.
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
