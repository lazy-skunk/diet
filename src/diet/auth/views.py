from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.wrappers import Response

from diet.auth.forms import (
    AccountInformationForm,
    ChangePasswordForm,
    SigninForm,
    SignupForm,
)
from diet.auth.service import (
    authenticate_user,
    register_user,
    update_password,
    update_username,
)
from diet.i18n import translate

blueprint = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/auth",
)


@blueprint.route("/signup", methods=["GET", "POST"])
def signup() -> str | Response:
    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        try:
            new_user = register_user(username, email, password)
        except (ValueError, TypeError):
            flash(translate("flash.email_registered"), "danger")
            return render_template("auth/signup.html", form=form)
        except SQLAlchemyError:
            flash(translate("flash.signup_failed"), "danger")
            return render_template("auth/signup.html", form=form)

        login_user(new_user)
        flash(translate("flash.signed_up"), "success")
        return redirect(url_for("body_composition.record_body_composition"))

    return render_template("auth/signup.html", form=form)


@blueprint.route("/signin", methods=["GET", "POST"])
def signin() -> str | Response:
    form = SigninForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = authenticate_user(email, password)

        if user:
            login_user(user)
            flash(translate("flash.signed_in"), "success")
            return redirect(url_for("main.index"))

        flash(translate("flash.signin_failed"), "danger")

    return render_template("auth/signin.html", form=form)


@blueprint.route("/signout", methods=["POST"])
@login_required
def signout() -> Response:
    logout_user()
    flash(translate("flash.signed_out"), "success")
    return redirect(url_for("main.index"))


@blueprint.route("/account_menu", methods=["GET"])
@login_required
def account_menu() -> str:
    return render_template("auth/account_menu.html")


@blueprint.route("/account_information", methods=["GET", "POST"])
@login_required
def account_information() -> str | Response:
    form = AccountInformationForm()
    if form.validate_on_submit():
        new_username = form.username.data
        try:
            update_username(current_user, new_username)
        except SQLAlchemyError:
            flash(translate("flash.username_failed"), "danger")
        else:
            flash(translate("flash.username_changed"), "success")
            return redirect(url_for("auth.account_information"))

    form.username.data = current_user.username
    return render_template("auth/account_information.html", form=form)


@blueprint.route("/change_email", methods=["GET"])
@login_required
def change_email() -> str | Response:
    return render_template("auth/change_email.html")


@blueprint.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password() -> str | Response:
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        try:
            update_password(current_user, current_password, new_password)
        except ValueError:
            flash(translate("flash.invalid_current_password"), "danger")
        except SQLAlchemyError:
            flash(translate("flash.password_failed"), "danger")
        else:
            flash(translate("flash.password_changed"), "success")
            return redirect(url_for("auth.account_menu"))

    return render_template("auth/change_password.html", form=form)


@blueprint.route("/deactivate_account", methods=["GET"])
@login_required
def deactivate_account() -> str | Response:
    return render_template("auth/deactivate_account.html")
