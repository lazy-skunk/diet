from copy import deepcopy
from typing import Any

import pytest
from pydantic import ValidationError

from diet.nutrition_optimizer.api_models import (
    ErrorResponse,
    OptimizeRequest,
    OptimizeResponse,
    validate_optimize_request,
)
from diet.nutrition_optimizer.models import (
    Constraint,
    FoodInformation,
    Objective,
)

_REQUEST_DATA: dict[str, Any] = {
    "foodSelections": [
        {
            "foodName": "boiled_egg",
            "energy": 134,
            "protein": 12.5,
            "fat": 10.4,
            "carbohydrates": 0.3,
            "minimumIntakeGrams": 50,
            "maximumIntakeGrams": 150,
        }
    ],
    "objective": {
        "sense": "maximize",
        "nutrient": "energy",
    },
    "constraints": [
        {
            "minMax": "max",
            "nutrient": "energy",
            "unit": "energy",
            "value": 1800,
        },
        {
            "minMax": "min",
            "nutrient": "protein",
            "unit": "amount",
            "value": 150,
        },
    ],
}


def test_error_response_uses_camel_case_error_code_alias() -> None:
    response = ErrorResponse(error_code="invalid_input")

    assert response.model_dump(by_alias=True) == {
        "status": "Error",
        "errorCode": "invalid_input",
    }


def test_error_response_rejects_unknown_error_code() -> None:
    with pytest.raises(ValidationError, match="Input should be"):
        ErrorResponse.model_validate({"errorCode": "unknown_error"})


def test_optimize_request_to_domain() -> None:
    optimize_request = OptimizeRequest.model_validate(_REQUEST_DATA)

    food_information, objective, constraints = optimize_request.to_domain()

    assert len(food_information) == 1
    assert isinstance(food_information[0], FoodInformation)
    assert isinstance(objective, Objective)
    assert len(constraints) == 2
    assert isinstance(constraints[0], Constraint)


def test_validate_optimize_request_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="Invalid request data: food_selections: Field required",
    ):
        validate_optimize_request({"objective": {"sense": "maximize"}})


@pytest.mark.parametrize(
    "invalid_value",
    [float("nan"), float("inf"), float("-inf")],
)
def test_validate_optimize_request_rejects_non_finite_values(
    invalid_value: float,
) -> None:
    request_data = deepcopy(_REQUEST_DATA)
    request_data["foodSelections"][0]["energy"] = invalid_value

    with pytest.raises(ValueError, match="Input should be a finite number"):
        validate_optimize_request(request_data)


def test_optimize_request_rejects_duplicate_food_names() -> None:
    duplicate_food = {**_REQUEST_DATA["foodSelections"][0]}
    request_data = {
        **_REQUEST_DATA,
        "foodSelections": [
            _REQUEST_DATA["foodSelections"][0],
            duplicate_food,
        ],
    }

    with pytest.raises(
        ValueError,
        match="food_selections: Value error, Food names must be unique.",
    ):
        validate_optimize_request(request_data)


def test_optimize_request_normalizes_food_name() -> None:
    request_data = deepcopy(_REQUEST_DATA)
    request_data["foodSelections"][0]["foodName"] = "  boiled_egg　"

    optimize_request = validate_optimize_request(request_data)

    assert optimize_request.food_selections[0].food_name == "boiled_egg"


def test_optimize_request_rejects_blank_food_name() -> None:
    request_data = deepcopy(_REQUEST_DATA)
    request_data["foodSelections"][0]["foodName"] = " 　"

    with pytest.raises(ValueError, match="Food name must be provided"):
        validate_optimize_request(request_data)


def test_optimize_request_rejects_duplicate_normalized_food_names() -> None:
    duplicate_food = {
        **_REQUEST_DATA["foodSelections"][0],
        "foodName": " boiled_egg ",
    }
    request_data = {
        **_REQUEST_DATA,
        "foodSelections": [
            _REQUEST_DATA["foodSelections"][0],
            duplicate_food,
        ],
    }

    with pytest.raises(ValueError, match="Food names must be unique"):
        validate_optimize_request(request_data)


def test_optimize_response_uses_camel_case_aliases() -> None:
    response = OptimizeResponse.model_validate(
        {
            "status": "Optimal",
            "food_intake_grams": {"boiled_egg": 100},
            "total_nutrient_values": {"energy": 201.0},
            "pfc_composition_ratio": {"protein": 25.0},
        }
    )

    dumped = response.model_dump(by_alias=True)

    assert "foodIntakeGrams" in dumped
    assert "totalNutrientValues" in dumped
    assert "pfcCompositionRatio" in dumped


def test_failed_optimize_response_uses_error_code_alias() -> None:
    response = OptimizeResponse.model_validate(
        {
            "status": "Infeasible",
            "error_code": "optimization_infeasible",
        }
    )

    assert response.model_dump(by_alias=True)["errorCode"] == (
        "optimization_infeasible"
    )


@pytest.mark.parametrize(
    "missing_result",
    [
        "food_intake_grams",
        "total_nutrient_values",
        "pfc_composition_ratio",
    ],
)
def test_optimal_response_requires_all_result_values(
    missing_result: str,
) -> None:
    response_data = {
        "status": "Optimal",
        "food_intake_grams": {"boiled_egg": 100},
        "total_nutrient_values": {"energy": 201.0},
        "pfc_composition_ratio": {"protein": 25.0},
    }
    del response_data[missing_result]

    with pytest.raises(
        ValidationError,
        match="An optimal response must include all result values.",
    ):
        OptimizeResponse.model_validate(response_data)


def test_optimal_response_rejects_error_code() -> None:
    with pytest.raises(
        ValidationError,
        match="An optimal response must not include an error code.",
    ):
        OptimizeResponse.model_validate(
            {
                "status": "Optimal",
                "food_intake_grams": {"boiled_egg": 100},
                "total_nutrient_values": {"energy": 201.0},
                "pfc_composition_ratio": {"protein": 25.0},
                "error_code": "optimization_failed",
            }
        )


def test_failed_response_requires_error_code() -> None:
    with pytest.raises(
        ValidationError,
        match="A failed response must include an error code.",
    ):
        OptimizeResponse.model_validate({"status": "Infeasible"})


def test_failed_response_rejects_result_values() -> None:
    with pytest.raises(
        ValidationError,
        match="A failed response must not include result values.",
    ):
        OptimizeResponse.model_validate(
            {
                "status": "Infeasible",
                "food_intake_grams": {},
                "error_code": "optimization_infeasible",
            }
        )


def test_optimize_request_forbids_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        OptimizeRequest.model_validate(
            {
                **_REQUEST_DATA,
                "unexpectedField": True,
            }
        )


def test_optimize_request_requires_food_information() -> None:
    with pytest.raises(ValidationError):
        OptimizeRequest.model_validate(
            {
                **_REQUEST_DATA,
                "foodSelections": [],
            }
        )


def test_constraint_value_accepts_decimal() -> None:
    request_data = {
        **_REQUEST_DATA,
        "constraints": [
            {
                "minMax": "min",
                "nutrient": "protein",
                "unit": "amount",
                "value": 12.5,
            }
        ],
    }

    optimize_request = OptimizeRequest.model_validate(request_data)
    _, _, constraints = optimize_request.to_domain()

    assert constraints[0].value == 12.5


def test_optimize_response_rejects_none_food_intake_grams() -> None:
    with pytest.raises(ValidationError):
        OptimizeResponse.model_validate(
            {
                "status": "Optimal",
                "food_intake_grams": {"boiled_egg": None},
                "total_nutrient_values": {"energy": 201.0},
                "pfc_composition_ratio": {"protein": 25.0},
            }
        )


def test_food_selection_to_food_information() -> None:
    request_data = {
        **_REQUEST_DATA,
        "foodSelections": [
            {
                "foodName": "manual tofu",
                "energy": 80,
                "protein": 7.0,
                "fat": 4.0,
                "carbohydrates": 2.0,
                "minimumIntakeGrams": 100,
                "maximumIntakeGrams": 200,
            }
        ],
    }

    optimize_request = OptimizeRequest.model_validate(request_data)
    food_information = optimize_request.food_selections[0].to_domain()

    assert food_information.name == "manual tofu"
    assert food_information.energy == 80
    assert food_information.maximum_intake_grams == 200


def test_manual_food_selection_requires_nutrient_values() -> None:
    request_data = {
        **_REQUEST_DATA,
        "foodSelections": [
            {
                "foodName": "manual tofu",
                "minimumIntakeGrams": 100,
                "maximumIntakeGrams": 200,
            }
        ],
    }

    with pytest.raises(ValidationError):
        OptimizeRequest.model_validate(request_data)
