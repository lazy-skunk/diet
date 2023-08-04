from datetime import date

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

from .forms import LogWeightForm, SignupForm
from .models import BodyComposition, db

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html", current_user=current_user)


@main.route("/log_weight", methods=["GET", "POST"])
def log_weight():
    today = date.today()
    user_id = 1  # ログイン機能実装まで固定値で誤魔化す。

    # 既存の記録があればその情報を表示し、無ければ新規登録フォームを表示する。
    existing_log = BodyComposition.query.filter_by(date=today, user_id=user_id).first()
    if existing_log:
        form = LogWeightForm(
            date=existing_log.date,
            weight=existing_log.weight,
            body_fat=existing_log.body_fat,
        )
    else:
        form = LogWeightForm()

    # 既存の記録があれば更新し、無ければ新規登録する。
    if form.validate_on_submit():
        log_date = form.date.data
        weight = form.weight.data
        body_fat = form.body_fat.data

        if existing_log:
            existing_log.weight = weight
            existing_log.body_fat = body_fat
        else:
            log = BodyComposition(
                date=log_date, weight=weight, body_fat=body_fat, user_id=user_id
            )
            db.session.add(log)

        db.session.commit()

        return redirect(url_for("main.index"))

    return render_template("log_weight.html", form=form, today=today)


@main.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        # 新規登録処理を行う（例：ユーザーデータをデータベースに保存するなど）
        print("#")
        # 登録が成功したらログインページにリダイレクトする（例：redirect(url_for("main.login")））
        # または、登録成功のメッセージを表示しても良い

    return render_template("signup.html", form=form, current_user=current_user)
