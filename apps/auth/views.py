from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.wrappers import Response

from apps.auth.forms import SigninForm, SignupForm
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

    return render_template(
        "auth/signup.html", form=form, current_user=current_user
    )


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

    return render_template(
        "auth/signin.html", form=form, current_user=current_user
    )


@blueprint.route("/signout")
@login_required
def signout() -> Response:
    logout_user()
    flash("Signed out successfully.", "success")
    return redirect(url_for("main.index"))
