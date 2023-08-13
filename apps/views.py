from datetime import date

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .forms import LogWeightForm, SigninForm, SignupForm
from .models import BodyComposition, User, db

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """メインページを表示します。

    Returns:
        - template: メインページのテンプレート。
    """
    return render_template("index.html", current_user=current_user)


@main.route("/log_weight", methods=["GET", "POST"])
@login_required
def log_weight():
    """
    体重および体脂肪率を記録または更新するページ。

    Returns:
        - template: 体重・体脂肪率のログ入力フォームを含むページのテンプレート。
    """
    user_id = current_user.id
    form = LogWeightForm()

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
            log = BodyComposition(
                date=log_date, weight=weight, body_fat=body_fat, user_id=user_id
            )
            db.session.add(log)

        db.session.commit()
        return redirect(url_for("main.index"))

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

    return render_template("log_weight.html", form=form)


@main.route("/signup", methods=["GET", "POST"])
def signup():
    """
    新規ユーザー登録のページ。

    Returns:
        - template: ユーザー登録フォームを含むページのテンプレート。
    """
    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        user = User(username=username, email=email, password=password)

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash("このユーザー名は既に登録されています。", "error")
        elif existing_email:
            flash("このメールアドレスは既に登録されています。", "error")
        else:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()

            flash("アカウントが作成されました。", "success")
            return redirect(url_for("main.index"))

    return render_template("signup.html", form=form, current_user=current_user)


@main.route("/signin", methods=["GET", "POST"])
def signin():
    """
    ユーザーログインページ。

    Returns:
        - template: ログインフォームを含むページのテンプレート。
    """
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
            flash("ログインに失敗しました。ユーザー名またはパスワードが間違っています", "error")

    return render_template("signin.html", form=form, current_user=current_user)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    """
    ユーザーログアウトのエンドポイント。ログアウト後、メインページにリダイレクトします。
    
    Returns:
        - redirect: メインページへのリダイレクトオブジェクト。
    """
    flash("ログアウトに成功しました。ご利用ありがとうございました。", "success")
    return redirect(url_for("main.index"))
