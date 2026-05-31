import pytest
from pydantic import ValidationError

from diet.nutrition_optimizer.api_models import (
    OptimizeRequest,
    OptimizeResponse,
    validate_optimize_request,
)
from diet.nutrition_optimizer.models import (
    Constraint,
    FoodInformation,
    Objective,
)

_REQUEST_DATA = {
    "foodInformation": [
        {
            "name": "boiled_egg",
            "energy": 134,
            "protein": 12.5,
            "fat": 10.4,
            "carbohydrates": 0.3,
            "gramsPerUnit": 50,
            "minimumIntake": 1,
            "maximumIntake": 3,
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
        match="Invalid request data: food_information: Field required",
    ):
        validate_optimize_request({"objective": {"sense": "maximize"}})


def test_optimize_response_uses_camel_case_aliases() -> None:
    response = OptimizeResponse.model_validate(
        {
            "status": "Optimal",
            "food_intakes": {"boiled_egg": 3},
            "total_nutrient_values": {"energy": 201.0},
            "pfc_ratio": {"protein": 25.0},
        }
    )

    dumped = response.model_dump(by_alias=True)

    assert "foodIntakes" in dumped
    assert "totalNutrientValues" in dumped
    assert "pfcRatio" in dumped


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
                "foodInformation": [],
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


def test_optimize_response_rejects_none_food_intake() -> None:
    with pytest.raises(ValidationError):
        OptimizeResponse.model_validate(
            {
                "status": "Optimal",
                "food_intakes": {"boiled_egg": None},
                "total_nutrient_values": {"energy": 201.0},
                "pfc_ratio": {"protein": 25.0},
            }
        )
