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
from wtforms.fields import FloatField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    NumberRange,
    Optional,
    ValidationError,
)


class CustomBodyFatFloatField(FloatField):
    """
    カスタムバリデーターを実装しても、デフォルトエラーメッセージが出力され、カスタムエラーメッセージは表示されなかった。
    この問題を解消するために、FloatField の設定を変更したクラスを作成した。
    """

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0])
            except ValueError:
                self.data = None
                raise ValidationError("体脂肪率には正の整数、または正の浮動小数点数を入力してください。")


class BaseLogBodyCompositionForm(FlaskForm):
    def validate_not_future_date(form, field):
        if field.data > date.today():
            raise ValidationError("今日以前の日付を選択してください。")

    today = date.today().isoformat()

    date = DateField(
        label="日付",
        validators=[DataRequired(message="日付を入力してください。"), validate_not_future_date],
        default=date.today,
        render_kw={"max": today},
    )

    weight = FloatField(
        label="体重 (kg)",
        validators=[
            DataRequired(message="体重を入力してください。"),
            NumberRange(min=0.1, max=999.9, message="体重は 0.1 から 999.9 の間で入力してください。"),
        ],
    )

    body_fat = CustomBodyFatFloatField(
        label="体脂肪率 (%)",
        validators=[
            Optional(),
            NumberRange(min=0, max=99.9, message="体脂肪率は 0 から 99.9 の間で入力してください。"),
        ],
    )


class LogBodyCompositionForm(BaseLogBodyCompositionForm):
    submit = SubmitField("記録")


class SignupForm(BaseLogBodyCompositionForm):
    username = StringField(
        label="ユーザー名", validators=[DataRequired(message="ユーザー名を入力してください。")]
    )
    email = StringField(
        label="Eメール", validators=[DataRequired(message="Eメールアドレスを入力してください。"), Email()]
    )
    password = PasswordField(
        label="パスワード", validators=[DataRequired(message="パスワードを入力してください。")]
    )
    confirm_password = PasswordField(
        label="パスワード (確認用)",
        validators=[
            DataRequired(message="パスワード (確認用) を入力してください。"),
            EqualTo("password", message="パスワードとパスワード (確認用) には同一の値を入力してください。"),
        ],
    )
    submit = SubmitField("登録")


class SigninForm(FlaskForm):
    username = StringField(
        label="ユーザー名", validators=[DataRequired(message="ユーザー名を入力してください。")]
    )
    password = PasswordField(
        label="パスワード", validators=[DataRequired(message="パスワードを入力してください。")]
    )
    submit = SubmitField("ログイン")
