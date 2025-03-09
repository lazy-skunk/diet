from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.wrappers import Response

from apps.auth.forms import (
    AccountInformationForm,
    ChangePasswordForm,
    SigninForm,
    SignupForm,
)
from apps.auth.service import UserService

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
            new_user = UserService.create(username, email, password)
            login_user(new_user)
            flash("Signed up successfully.", "success")
            return redirect(
                url_for("body_composition.record_body_composition")
            )
        except (ValueError, TypeError) as e:
            flash(str(e), "danger")
        except SQLAlchemyError:
            flash("Sign-up failed. Please try again later.", "danger")

    return render_template("auth/signup.html", form=form)


@blueprint.route("/signin", methods=["GET", "POST"])
def signin() -> str | Response:
    form = SigninForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = UserService.authenticate(email, password)

        if user:
            login_user(user)
            flash("Signed in successfully.", "success")
            return redirect(url_for("main.index"))

        flash("Sign-in failed. Invalid email or password.", "danger")

    return render_template("auth/signin.html", form=form)


@blueprint.route("/signout")
@login_required
def signout() -> Response:
    logout_user()
    flash("Signed out successfully.", "success")
    return redirect(url_for("main.index"))


@blueprint.route("/account_menu", methods=["GET"])
@login_required
def account_menu() -> str:
    return render_template("auth/account_menu.html")


@blueprint.route("/account_information", methods=["GET", "POST"])
@login_required
def account_information() -> str:
    form = AccountInformationForm()
    if form.validate_on_submit():
        new_username = form.username.data
        UserService.change_username(current_user, new_username)
        flash("Usename changed successfully.", "success")

    form.username.data = current_user.username
    return render_template("auth/account_information.html", form=form)


@blueprint.route("/change_email", methods=["GET"])
@login_required
def change_email() -> str | Response:
    # TODO: 未実装
    return render_template("auth/change_email.html")


@blueprint.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password() -> str | Response:
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        is_succeeded = UserService.change_password(
            current_user, current_password, new_password
        )

        if is_succeeded:
            flash("Password changed successfully.", "success")
            return render_template("auth/account_menu.html")
        else:
            flash("Invalid current password.", "danger")

    return render_template("auth/change_password.html", form=form)


@blueprint.route("/deactivate_account", methods=["GET"])
@login_required
def deactivate_account() -> str | Response:
    # TODO: 未実装
    return render_template("auth/deactivate_account.html")
