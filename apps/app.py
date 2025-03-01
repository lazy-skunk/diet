import sys
from typing import Any

from flask import Flask, g, render_template, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import current_user
from flask_migrate import Migrate

from apps.config import config
from apps.extensions import csrf_protect, login_manager, sql_alchemy
from apps.utils.custom_logger import CustomLogger

_logger = CustomLogger.get_logger()


def create_app(config_key: str) -> Flask:
    _logger.info("Start")

    try:
        app = Flask(__name__)
        app.config.from_object(config[config_key])

        _init_debug_toolbar(app, config_key)
        _init_database(app)
        _init_csrf_protect(app)
        _init_login_manager(app)

        _register_blueprints(app)
        _register_error_handlers(app)

        _register_request_hooks(app)
    except Exception as e:
        _logger.error(e, exc_info=True)
        sys.exit(1)

    _logger.info("End")
    return app


def _init_debug_toolbar(app: Flask, config_key: str) -> None:
    if config_key == "local":
        DebugToolbarExtension(app)
        app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False


def _init_database(app: Flask) -> None:
    sql_alchemy.init_app(app)
    Migrate(app, sql_alchemy)


def _init_csrf_protect(app: Flask) -> None:
    csrf_protect.init_app(app)


def _init_login_manager(app: Flask) -> None:
    login_manager.init_app(app)
    login_manager.login_view = "auth.signin"
    login_manager.login_message = ""

    _register_user_loader()


def _register_user_loader() -> None:
    from apps.auth.models import User

    @login_manager.user_loader
    def load_user(user_id: str) -> User:
        return User.query.get(int(user_id))


def _register_blueprints(app: Flask) -> None:
    from apps.auth.views import blueprint as auth_blueprint
    from apps.body_composition.views import (
        blueprint as body_composition_blueprint,
    )
    from apps.views import blueprint as main_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(body_composition_blueprint)


def _register_request_hooks(app: Flask) -> None:
    @app.before_request
    def before_request() -> None:
        g.user = current_user


def _register_error_handlers(app: Flask) -> None:
    app.register_error_handler(404, _page_not_found)
    app.register_error_handler(500, _internal_server_error)


def _page_not_found(e: Any) -> tuple[str, int]:
    _logger.info(f"404 Not Found: {request.path}")
    return render_template("404.html"), 404


def _internal_server_error(e: Any) -> tuple[str, int]:
    _logger.error(
        f"500 Internal Server Error: {request.path}, Error: {e}", exc_info=True
    )
    return render_template("500.html"), 500
