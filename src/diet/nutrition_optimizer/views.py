from flask import Blueprint, Response, jsonify, render_template, request

from diet.nutrition_optimizer.optimizer.nutrition_optimizer import (
    NutritionOptimizer,
)
from diet.nutrition_optimizer.optimizer.utilities import (
    convert_top_level_keys_to_camel_case,
    parse_request_data,
)
from diet.utils.custom_logger import CustomLogger

blueprint = Blueprint(
    "nutrition_optimizer",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/nutrition_optimizer",
)

_logger = CustomLogger.get_logger()


@blueprint.route("/")
def index() -> str:
    return render_template("nutrition_optimizer/index.html")


@blueprint.route("/optimize", methods=["POST"])
def optimize() -> Response:
    try:
        food_information, objective, constraints = parse_request_data(request)

        nutrition_optimizer = NutritionOptimizer(
            food_information, objective, constraints
        )
        result = nutrition_optimizer.solve()

        parsed_result = convert_top_level_keys_to_camel_case(result)
        return jsonify(parsed_result)
    except ValueError as e:
        _logger.warning(f"Invalid request data: {e}")
        return jsonify({"status": "Error", "message": "Invalid request data"})
    except Exception as e:  # pragma: no cover
        _logger.warning(f"Error during optimization: {e}")
        return jsonify({"status": "Error", "message": str(e)})
