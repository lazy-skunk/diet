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
            NumberRange(min=0.1, max=300.0),
        ],
        render_kw={
            "class": "form-control",
            "type": "number",
            "min": "0.1",
            "max": "300.0",
            "step": 0.1,
        },
    )
    body_fat = FloatField(
        validators=[
            Optional(),
            NumberRange(min=0.1, max=99.9),
        ],
        render_kw={
            "class": "form-control",
            "type": "number",
            "min": "0.1",
            "max": "99.9",
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
