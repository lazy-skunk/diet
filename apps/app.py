from flask import Flask, g, render_template
from flask_login import LoginManager, current_user

from .config import config
from .models import User, db


def create_app(config_key):
    app = Flask(__name__)
    app.config.from_object(config[config_key])

    db.init_app(app)

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "main.signin"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.init_app(app)

    from .views import main

    app.register_blueprint(main)

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    @app.before_request
    def before_request():
        g.user = current_user

    return app


def page_not_found(e):
    return render_template("404.html"), 404


def internal_server_error(e):
    return render_template("500.html"), 500
