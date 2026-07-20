from flask import Blueprint, Response, jsonify, render_template, request
from flask_wtf.csrf import CSRFError

from diet.i18n import translate
from diet.nutrition_optimizer.api_models import (
    ErrorCode,
    ErrorResponse,
    OptimizeRequest,
    OptimizeResponse,
    validate_optimize_request,
)
from diet.nutrition_optimizer.nutrients import (
    NUTRIENT_REFERENCE_GRAMS,
    NUTRIENTS,
    NutrientDefinition,
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


@blueprint.errorhandler(CSRFError)
def handle_csrf_error(error: CSRFError) -> tuple[Response, int]:
    _logger.warning(f"CSRF validation failed: {error.description}")
    return _error_response("request_verification_failed", 400)


@blueprint.route("/")
def index() -> str:
    return render_template(
        "nutrition_optimizer/index.html",
        nutrient_definitions=[
            _nutrient_definition_item(definition) for definition in NUTRIENTS
        ],
    )


@blueprint.route("/optimize", methods=["POST"])
def optimize() -> Response | tuple[Response, int]:
    try:
        payload = request.get_json(silent=True)
        optimize_request = _parse_optimize_request(payload)
        domain_input = optimize_request.to_domain()
    except ValueError as e:
        _logger.warning(f"Invalid request data: {e}")
        return _error_response("invalid_input", 400)

    try:
        result = optimize_nutrition(*domain_input)
        response = OptimizeResponse.from_domain_result(result)
        return jsonify(response.model_dump(by_alias=True))
    except Exception as e:
        _logger.error(f"Error during optimization: {e}", exc_info=True)
        return _error_response("unexpected_response", 500)


def _parse_optimize_request(payload: object) -> OptimizeRequest:
    if payload is None:
        raise ValueError("Invalid request data: request JSON is required")

    return validate_optimize_request(payload)


def _error_response(
    error_code: ErrorCode, status_code: int
) -> tuple[Response, int]:
    response = ErrorResponse(error_code=error_code)
    return jsonify(response.model_dump(by_alias=True)), status_code


def _nutrient_definition_item(
    definition: NutrientDefinition,
) -> dict[str, str]:
    return {
        "identifier": definition.food_master_identifier,
        "key": definition.key,
        "name": translate(definition.translation_key),
        "unit": definition.unit,
        "displayUnit": (f"{definition.unit}/{NUTRIENT_REFERENCE_GRAMS}g"),
    }
