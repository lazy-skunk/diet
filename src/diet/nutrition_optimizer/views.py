from flask import Blueprint, Response, jsonify, render_template, request

from diet.nutrition_optimizer.service import optimize as optimize_nutrition
from diet.utils.custom_logger import get_logger

blueprint = Blueprint(
    "nutrition_optimizer",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/nutrition_optimizer",
)

_logger = get_logger()


@blueprint.route("/")
def index() -> str:
    return render_template("nutrition_optimizer/index.html")


@blueprint.route("/optimize", methods=["POST"])
def optimize() -> Response | tuple[Response, int]:
    try:
        return jsonify(optimize_nutrition(request))
    except ValueError as e:
        _logger.warning(f"Invalid request data: {e}")
        return (
            jsonify({"status": "Error", "message": "Invalid request data"}),
            400,
        )
    except Exception as e:
        _logger.warning(f"Error during optimization: {e}")
        return jsonify({"status": "Error", "message": str(e)}), 500
