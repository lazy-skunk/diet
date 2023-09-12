import random
from datetime import date, datetime, timedelta
import json

import pandas as pd
from flask import Blueprint, flash, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .forms import LogBodyCompositionForm, SigninForm, SignupForm
from .models import BodyComposition, User, db

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html", current_user=current_user)


@main.route("/log_body_composition", methods=["GET", "POST"])
@login_required
def log_body_composition():
    user_id = current_user.id
    form = LogBodyCompositionForm()

    # フォーム入力時処理
    if form.validate_on_submit():
        log_date = form.date.data
        weight = form.weight.data
        body_fat = form.body_fat.data

        specified_date_log = BodyComposition.query.filter_by(
            date=form.date.data, user_id=user_id
        ).first()

        if specified_date_log:
            specified_date_log.weight = weight
            specified_date_log.body_fat = body_fat
        else:
            try:
                log = BodyComposition(
                    date=log_date, weight=weight, body_fat=body_fat, user_id=user_id
                )
                db.session.add(log)
            except Exception as e:
                flash(f"{str(e)}", "danger")
                return render_template(
                    "log_body_composition.html",
                    form=form,
                )

        try:
            db.session.commit()
            return redirect(url_for("main.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"予期せぬエラーが発生しました。: {str(e)}", "danger")
            return render_template("log_body_composition.html", form=form)

    # フォーム初期値設定
    today = date.today()
    todays_log = BodyComposition.query.filter_by(date=today, user_id=user_id).first()

    if todays_log:
        form.weight.data = todays_log.weight
        form.body_fat.data = todays_log.body_fat
    else:
        last_registered_log = (
            BodyComposition.query.filter_by(user_id=user_id)
            .order_by(BodyComposition.date.desc())
            .first()
        )
        if last_registered_log:
            form.weight.data = last_registered_log.weight
            form.body_fat.data = last_registered_log.body_fat

    return render_template("log_body_composition.html", form=form)


@main.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        log_date = form.date.data
        weight = form.weight.data
        body_fat = form.body_fat.data

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash("別のユーザー名を入力してください。このユーザー名は既に登録されています。", "danger")
        elif existing_email:
            flash("別のメールアドレスを入力してください。このメールアドレスは既に登録されています。", "danger")
        else:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()

            body_composition = BodyComposition(
                date=log_date, weight=weight, body_fat=body_fat, user_id=user.id
            )
            db.session.add(body_composition)
            db.session.commit()

            login_user(user)
            flash("アカウントが作成され、体重が登録されました。", "success")
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
            flash("ログインに成功しました。", "success")
            return redirect(url_for("main.index"))
        else:
            flash("ログインに失敗しました。ユーザー名またはパスワードが誤っています。", "danger")

    return render_template("signin.html", form=form, current_user=current_user)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ログアウトに成功しました。ご利用ありがとうございました。", "success")
    return redirect(url_for("main.index"))


@main.route("/get_body_composition_data", methods=["GET"])
def fetch_body_composition_data():
    if current_user.is_authenticated:
        user_id = current_user.id
        body_composition_objects = get_body_compositions(user_id)
        body_composition_object_lists = convert_objects_to_object_lists(
            body_composition_objects
        )
    else:
        body_composition_object_lists = generate_dummy_data_object_list()

    body_composition_df = pd.DataFrame(body_composition_object_lists)
    body_composition_df["date"] = pd.to_datetime(body_composition_df["date"])
    body_composition_df.set_index("date", inplace=True)
    monthly_averages_and_weight_change_rates_df = (
        compute_monthly_averages_and_weight_change_rates(body_composition_df)
    )
    monthly_averages_and_weight_change_rates_json = convert_dataframe_to_json(
        monthly_averages_and_weight_change_rates_df
    )

    return jsonify(
        body_composition_object_lists, monthly_averages_and_weight_change_rates_json
    )


def get_body_compositions(user_id):
    body_composition_objects = (
        BodyComposition.query.filter_by(user_id=user_id)
        .order_by(BodyComposition.date.asc())
        .all()
    )
    return body_composition_objects


def convert_objects_to_object_lists(body_composition_objects):
    body_composition_object_lists = [
        {
            "date": bco.date.strftime("%Y-%m-%d"),
            "weight": bco.weight,
            "body_fat": bco.body_fat,
        }
        for bco in body_composition_objects
    ]
    return body_composition_object_lists


def compute_monthly_averages_and_weight_change_rates(body_composition_df):
    monthly_averages_and_weight_change_rates_df = (
        body_composition_df.resample("M").mean().round(2)
    )

    monthly_averages_and_weight_change_rates_df["weight_change_rate"] = (
        (
            monthly_averages_and_weight_change_rates_df["weight"]
            - monthly_averages_and_weight_change_rates_df["weight"].shift(1)
        )
        / monthly_averages_and_weight_change_rates_df["weight"].shift(1)
        * 100
    ).round(2)

    monthly_averages_and_weight_change_rates_df.reset_index(inplace=True)
    monthly_averages_and_weight_change_rates_df[
        "date"
    ] = monthly_averages_and_weight_change_rates_df["date"].dt.strftime("%Y-%m")

    return monthly_averages_and_weight_change_rates_df


def convert_dataframe_to_json(df):
    json_data = df.to_json(orient="records")
    return json.loads(json_data)


def generate_dummy_data_object_list():
    duration = 365 * 3
    today = datetime.now()
    date = today - timedelta(days=int(duration))

    weight = round(random.uniform(90, 100), 2)
    body_fat = round(random.uniform(25, 30), 2)

    body_composition_object_lists = []
    while date <= today:
        weight_variation = round(random.uniform(-0.4, 0.36), 2)
        weight = round(max(weight + weight_variation, 50), 2)

        body_fat_variation = round(random.uniform(-0.2, 0.18), 2)
        body_fat = round(max(body_fat + body_fat_variation, 5), 2)

        body_composition_object = {
            "date": date.strftime("%Y-%m-%d"),
            "weight": weight,
            "body_fat": body_fat,
        }
        body_composition_object_lists.append(body_composition_object)

        date += timedelta(days=1)

    return body_composition_object_lists
