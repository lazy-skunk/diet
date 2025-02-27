from flask import Blueprint, render_template
from flask_login import current_user

blueprint = Blueprint(
    "main", __name__, template_folder="templates", static_folder="static"
)


@blueprint.route("/")
def index() -> str:
    return render_template("index.html", current_user=current_user)
