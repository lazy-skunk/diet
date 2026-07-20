import pytest
from pydantic import ValidationError

from diet.api_models import ApiModel


class ExampleApiModel(ApiModel):
    body_fat: float
    food_selections: list[str]
    pfc_composition_ratio: dict[str, float]
    error_code: str


def test_api_model_accepts_field_names_and_serializes_aliases() -> None:
    model = ExampleApiModel(
        body_fat=20.0,
        food_selections=["tofu"],
        pfc_composition_ratio={"protein": 30.0},
        error_code="invalid_input",
    )

    assert model.model_dump(by_alias=True) == {
        "bodyFat": 20.0,
        "foodSelections": ["tofu"],
        "pfcCompositionRatio": {"protein": 30.0},
        "errorCode": "invalid_input",
    }


def test_api_model_accepts_aliases() -> None:
    model = ExampleApiModel.model_validate(
        {
            "bodyFat": 20.0,
            "foodSelections": ["tofu"],
            "pfcCompositionRatio": {"protein": 30.0},
            "errorCode": "invalid_input",
        }
    )

    assert model.body_fat == 20.0
    assert model.food_selections == ["tofu"]


def test_api_model_rejects_extra_fields() -> None:
    with pytest.raises(
        ValidationError, match="Extra inputs are not permitted"
    ):
        ExampleApiModel.model_validate(
            {
                "bodyFat": 20.0,
                "foodSelections": ["tofu"],
                "pfcCompositionRatio": {"protein": 30.0},
                "errorCode": "invalid_input",
                "unknownField": "value",
            }
        )


@pytest.mark.parametrize(
    "invalid_value", [float("nan"), float("inf"), float("-inf")]
)
def test_api_model_rejects_non_finite_numbers(invalid_value: float) -> None:
    with pytest.raises(
        ValidationError, match="Input should be a finite number"
    ):
        ExampleApiModel.model_validate(
            {
                "bodyFat": invalid_value,
                "foodSelections": ["tofu"],
                "pfcCompositionRatio": {"protein": 30.0},
                "errorCode": "invalid_input",
            }
        )
