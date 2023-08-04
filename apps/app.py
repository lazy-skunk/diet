from apps.config import config
from dash import Dash
from flask import Flask, render_template

from .dash_app import init_dash
from .models import db


def create_app(config_key):
    app = Flask(__name__)
    app.config.from_object(config[config_key])

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from .views import main

    app.register_blueprint(main)

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    app_dash = Dash(server=app, url_base_pathname="/dash/")
    init_dash(app_dash)

    return app


def page_not_found(e):
    return render_template("404.html"), 404


def internal_server_error(e):
    return render_template("500.html"), 500
