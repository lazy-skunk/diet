from datetime import date
from typing import Any

from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField
from wtforms.fields import FloatField
from wtforms.validators import (
    DataRequired,
    InputRequired,
    NumberRange,
    Optional,
)

from diet.body_composition.constants import (
    MAX_BODY_FAT,
    MAX_WEIGHT,
    MIN_BODY_FAT,
    MIN_WEIGHT,
)


def _today() -> date:
    return date.today()


class RecordBodyCompositionForm(FlaskForm):
    date = DateField(
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )
    weight = FloatField(
        validators=[
            InputRequired(),
            NumberRange(min=MIN_WEIGHT, max=MAX_WEIGHT),
        ],
        render_kw={
            "class": "form-control",
            "type": "number",
            "min": str(MIN_WEIGHT),
            "max": str(MAX_WEIGHT),
            "step": 0.1,
        },
    )
    body_fat = FloatField(
        validators=[
            Optional(),
            NumberRange(min=MIN_BODY_FAT, max=MAX_BODY_FAT),
        ],
        render_kw={
            "class": "form-control",
            "type": "number",
            "min": str(MIN_BODY_FAT),
            "max": str(MAX_BODY_FAT),
            "step": 0.1,
        },
    )
    submit = SubmitField(
        render_kw={"class": "btn btn-primary"},
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        today = _today()
        if self.date.data is None:
            self.date.data = today

        self.date.render_kw = {
            **(self.date.render_kw or {}),
            "max": today.isoformat(),
        }
