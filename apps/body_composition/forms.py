from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField
from wtforms.fields import FloatField
from wtforms.validators import (
    DataRequired,
    NumberRange,
    Optional,
    ValidationError,
)


class CustomBodyFatFloatField(FloatField):
    """
    カスタムバリデーターを実装しても、デフォルトエラーメッセージが出力され、カスタムエラーメッセージは表示されなかった。
    この問題を解消するために、FloatField の設定を変更したクラスを作成した。
    """

    def process_formdata(self, valuelist: list) -> None:
        if valuelist:
            try:
                self.data: float | None = float(valuelist[0])
            except ValueError:
                self.data = None
                raise ValidationError(
                    "体脂肪率には正の整数、または正の浮動小数点数を入力してください。"
                )


class BaseLogBodyCompositionForm(FlaskForm):
    def validate_not_future_date(
        form: "BaseLogBodyCompositionForm", field: DateField
    ) -> None:
        if field.data > date.today():
            raise ValidationError("今日以前の日付を選択してください。")

    today = date.today().isoformat()

    date = DateField(
        label="日付",
        validators=[
            DataRequired(message="日付を入力してください。"),
            validate_not_future_date,
        ],
        default=date.today,
        render_kw={"max": today},
    )

    weight = FloatField(
        label="体重 (kg)",
        validators=[
            DataRequired(message="体重を入力してください。"),
            NumberRange(
                min=0.1,
                max=999.9,
                message="体重は 0.1 から 999.9 の間で入力してください。",
            ),
        ],
    )

    body_fat = CustomBodyFatFloatField(
        label="体脂肪率 (%)",
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=99.9,
                message="体脂肪率は 0 から 99.9 の間で入力してください。",
            ),
        ],
    )


class LogBodyCompositionForm(BaseLogBodyCompositionForm):
    submit = SubmitField("記録")
