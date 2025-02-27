from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class BaseAuthForm(FlaskForm):
    email = StringField(
        validators=[DataRequired(), Email()],
        render_kw={"class": "form-control", "autocomplete": "username"},
    )
    password = PasswordField(
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )

    def _order_fields(self, order: list[str]) -> None:
        ordered_fields = {
            field_name: self._fields[field_name]  # type: ignore
            for field_name in order
            if field_name in self._fields  # type: ignore
        }
        self._fields = ordered_fields


class SignupForm(BaseAuthForm):
    username = StringField(
        validators=[DataRequired(), Length(min=1, max=255)],
        render_kw={"class": "form-control", "autocomplete": "username"},
    )
    confirm_password = PasswordField(
        validators=[DataRequired(), EqualTo("password")],
        render_kw={"class": "form-control", "autocomplete": "new-password"},
    )
    submit = SubmitField(
        render_kw={"class": "btn btn-primary"},
    )

    def __init__(self) -> None:
        super().__init__()
        self._post_init()

    def _post_init(self) -> None:
        self.password.render_kw["autocomplete"] = "new-password"

        order = [
            "csrf_token",
            "username",
            "email",
            "password",
            "confirm_password",
            "submit",
        ]
        self._order_fields(order)


class SigninForm(BaseAuthForm):
    submit = SubmitField(
        render_kw={"class": "btn btn-primary"},
    )

    def __init__(self) -> None:
        super().__init__()
        self._post_init()

    def _post_init(self) -> None:
        self.password.render_kw["autocomplete"] = "current-password"
