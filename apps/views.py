from datetime import date

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .forms import LogWeightForm, SigninForm, SignupForm
from .models import BodyComposition, User, db

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html", current_user=current_user)


@main.route("/log_weight", methods=["GET", "POST"])
@login_required
def log_weight():
    today = date.today()
    user_id = current_user.id
    existing_log = BodyComposition.query.filter_by(date=today, user_id=user_id).first()

    if existing_log:
        form = LogWeightForm(
            date=existing_log.date,
            weight=existing_log.weight,
            body_fat=existing_log.body_fat,
        )
    else:
        form = LogWeightForm()

    if form.validate_on_submit():
        log_date = form.date.data
        weight = form.weight.data
        body_fat = form.body_fat.data

        existing_log = BodyComposition.query.filter_by(
            date=log_date, user_id=user_id
        ).first()

        if existing_log:
            existing_log.weight = weight
            existing_log.body_fat = body_fat
        else:
            log = BodyComposition(
                date=log_date, weight=weight, body_fat=body_fat, user_id=user_id
            )
            db.session.merge(log)

        db.session.commit()

        return redirect(url_for("main.index"))

    return render_template("log_weight.html", form=form, today=today)


@main.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        user = User(username=username, email=email, password=password)

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash("このユーザー名は既に登録されています", "error")
        elif existing_email:
            flash("このメールアドレスは既に登録されています", "error")
        else:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()

            flash("アカウントが作成されました", "success")
            return redirect(url_for("main.index"))

    return render_template("signup.html", form=form, current_user=current_user)


@main.route("/signin", methods=["GET", "POST"])
def signin():
    form = SigninForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("ログインに成功しました", "success")
            return redirect(url_for("main.index"))
        else:
            flash("ログインに失敗しました。ユーザー名またはパスワードが間違っています", "error")

    return render_template("signin.html", form=form, current_user=current_user)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
