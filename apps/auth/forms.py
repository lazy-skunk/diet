from typing import Any

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
        original_fields = self._fields  # type: ignore

        ordered_fields = {
            field_name: self._fields[field_name]  # type: ignore
            for field_name in order
            if field_name in self._fields  # type: ignore
        }

        for field_name in original_fields.keys():
            if field_name not in ordered_fields:
                ordered_fields[field_name] = original_fields[field_name]

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
    sign_up = SubmitField(
        render_kw={"class": "btn btn-primary"},
    )

    def __init__(self) -> None:
        super().__init__()
        self._post_init()

    def _post_init(self) -> None:
        self.password.render_kw["autocomplete"] = "new-password"

        order = [
            "username",
            "email",
            "password",
            "confirm_password",
        ]
        self._order_fields(order)


class SigninForm(BaseAuthForm):
    sign_in = SubmitField(
        render_kw={"class": "btn btn-primary"},
    )

    def __init__(self) -> None:
        super().__init__()
        self._post_init()

    def _post_init(self) -> None:
        self.password.render_kw["autocomplete"] = "current-password"


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "autocomplete": "current-password",
        },
    )
    new_password = PasswordField(
        validators=[DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "new-password"},
    )
    confirm_new_password = PasswordField(
        validators=[DataRequired(), EqualTo("new_password")],
        render_kw={"class": "form-control", "autocomplete": "new-password"},
    )
    change_password = SubmitField(
        render_kw={"class": "btn btn-primary"},
    )


class AccountInformationForm(FlaskForm):
    username = StringField(
        validators=[DataRequired(), Length(min=1, max=255)],
        render_kw={"class": "form-control", "autocomplete": "username"},
    )
    update = SubmitField(
        render_kw={"class": "btn btn-primary"},
    )
