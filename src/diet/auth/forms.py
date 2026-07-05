from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from diet.auth.constants import USERNAME_MAX_LENGTH
from diet.i18n import translate


def normalize_email(email: str | None) -> str | None:
    if email is None:
        return None
    return email.strip().lower()


class BaseAuthForm(FlaskForm):
    email = StringField(
        filters=[normalize_email],
        render_kw={"class": "form-control", "autocomplete": "username"},
    )
    password = PasswordField(
        render_kw={"class": "form-control"},
    )

    def __init__(self) -> None:
        super().__init__()
        self.email.label.text = translate("form.email")
        self.email.validators = [
            DataRequired(message=translate("validation.required")),
            Email(message=translate("validation.email")),
        ]
        self.password.label.text = translate("form.password")
        self.password.validators = [
            DataRequired(message=translate("validation.required")),
        ]

    def _order_fields(self, order: list[str]) -> None:
        original_fields = self._fields  # type: ignore

        ordered_fields = {
            field_name: self._fields[field_name]  # type: ignore
            for field_name in order
            if field_name in self._fields  # type: ignore
        }

        for field_name in original_fields:
            if field_name not in ordered_fields:
                ordered_fields[field_name] = original_fields[field_name]

        self._fields = ordered_fields


class SignupForm(BaseAuthForm):
    username = StringField(
        render_kw={"class": "form-control", "autocomplete": "username"},
    )
    confirm_password = PasswordField(
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
        self.username.label.text = translate("form.username")
        self.username.validators = [
            DataRequired(message=translate("validation.required")),
            Length(
                min=1,
                max=USERNAME_MAX_LENGTH,
                message=translate("validation.length_between"),
            ),
        ]
        self.confirm_password.label.text = translate("form.confirm_password")
        self.confirm_password.validators = [
            DataRequired(message=translate("validation.required")),
            EqualTo("password", message=translate("validation.equal_to")),
        ]
        self.sign_up.label.text = translate("form.sign_up")
        self.sign_up.render_kw = {
            **(self.sign_up.render_kw or {}),
            "value": translate("form.sign_up"),
        }

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
        self.sign_in.label.text = translate("form.sign_in")
        self.sign_in.render_kw = {
            **(self.sign_in.render_kw or {}),
            "value": translate("form.sign_in"),
        }


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        render_kw={
            "class": "form-control",
            "autocomplete": "current-password",
        },
    )
    new_password = PasswordField(
        render_kw={"class": "form-control", "autocomplete": "new-password"},
    )
    confirm_new_password = PasswordField(
        render_kw={"class": "form-control", "autocomplete": "new-password"},
    )
    change_password = SubmitField(
        render_kw={"class": "btn btn-primary"},
    )

    def __init__(self) -> None:
        super().__init__()
        self.current_password.label.text = translate("form.current_password")
        self.current_password.validators = [
            DataRequired(message=translate("validation.required")),
        ]
        self.new_password.label.text = translate("form.new_password")
        self.new_password.validators = [
            DataRequired(message=translate("validation.required")),
        ]
        self.confirm_new_password.label.text = translate(
            "form.confirm_new_password"
        )
        self.confirm_new_password.validators = [
            DataRequired(message=translate("validation.required")),
            EqualTo(
                "new_password",
                message=translate("validation.equal_to"),
            ),
        ]
        self.change_password.label.text = translate("form.change_password")
        self.change_password.render_kw = {
            **(self.change_password.render_kw or {}),
            "value": translate("form.change_password"),
        }


class AccountInformationForm(FlaskForm):
    username = StringField(
        render_kw={"class": "form-control", "autocomplete": "username"},
    )
    update = SubmitField(
        render_kw={"class": "btn btn-primary"},
    )

    def __init__(self) -> None:
        super().__init__()
        self.username.label.text = translate("form.username")
        self.username.validators = [
            DataRequired(message=translate("validation.required")),
            Length(
                min=1,
                max=USERNAME_MAX_LENGTH,
                message=translate("validation.length_between"),
            ),
        ]
        self.update.label.text = translate("form.update")
        self.update.render_kw = {
            **(self.update.render_kw or {}),
            "value": translate("form.update"),
        }
