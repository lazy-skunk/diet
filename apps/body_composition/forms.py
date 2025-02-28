from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField
from wtforms.fields import FloatField
from wtforms.validators import DataRequired, NumberRange, Optional

today = date.today()


class LogBodyCompositionForm(FlaskForm):
    date = DateField(
        validators=[DataRequired()],
        default=today,
        render_kw={"class": "form-control", "max": today},
    )
    weight = FloatField(
        validators=[
            DataRequired(),
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
            NumberRange(min=0, max=99.9),
        ],
        render_kw={
            "class": "form-control",
            "type": "number",
            "min": "0",
            "max": "99.9",
            "step": 0.1,
        },
    )
    submit = SubmitField(
        render_kw={"class": "btn btn-primary"},
    )
