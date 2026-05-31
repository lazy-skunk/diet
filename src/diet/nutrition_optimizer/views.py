from flask import Blueprint, Response, jsonify, render_template, request

from diet.nutrition_optimizer.api_models import (
    OptimizeRequest,
    OptimizeResponse,
    validate_optimize_request,
)
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
        payload = request.get_json(silent=True)
        optimize_request = _parse_optimize_request(payload)
        result = optimize_nutrition(*optimize_request.to_domain())
        response = OptimizeResponse.from_domain_result(result)
        return jsonify(response.model_dump(by_alias=True))
    except ValueError as e:
        _logger.warning(f"Invalid request data: {e}")
        return (
            jsonify({"status": "Error", "message": "Invalid request data"}),
            400,
        )
    except Exception as e:
        _logger.warning(f"Error during optimization: {e}")
        return jsonify({"status": "Error", "message": str(e)}), 500


def _parse_optimize_request(payload: object) -> OptimizeRequest:
    if payload is None:
        raise ValueError("Invalid request data: request JSON is required")

    return validate_optimize_request(payload)
