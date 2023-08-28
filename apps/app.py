from flask import Flask, g, render_template
from flask_login import LoginManager, current_user

from .config import config
from .models import User, db


def create_app(config_key):
    """
    Flaskアプリケーションのインスタンスを作成し、設定および初期化を行います。

    Parameters:
    - config_key (str): 使用する設定のキー。

    Returns:
    - Flask: 初期化されたFlaskアプリケーションインスタンス。

    Notes:
    この関数は、Flaskのファクトリーパターンに従ってアプリケーションを作成します。
    また、関連するコンポーネントや拡張機能も初期化します。
    """
    app = Flask(__name__)
    app.config.from_object(config[config_key])

    db.init_app(app)

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "main.signin"

    @login_manager.user_loader
    def load_user(user_id):
        """指定されたユーザーIDに関連するユーザーをロードする関数。"""
        return User.query.get(int(user_id))

    login_manager.init_app(app)

    from .views import main

    app.register_blueprint(main)

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    @app.before_request
    def before_request():
        """各リクエスト前に実行される関数。現在のユーザーをglobalオブジェクトに保存します。"""
        g.user = current_user

    return app


def page_not_found(e):
    """
    404エラー時のエラーハンドラ関数。

    Parameters:
    - e (Exception): 例外オブジェクト。

    Returns:
    - tuple: 404エラーページのテンプレートとHTTPステータスコード。
    """
    return render_template("404.html"), 404


def internal_server_error(e):
    """
    500エラー時のエラーハンドラ関数。

    Parameters:
    - e (Exception): 例外オブジェクト。

    Returns:
    - tuple: 500エラーページのテンプレートとHTTPステータスコード。
    """
    return render_template("500.html"), 500
