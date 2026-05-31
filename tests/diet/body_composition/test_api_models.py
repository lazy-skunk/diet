import pytest
from pydantic import ValidationError

from diet.body_composition.api_models import (
    BodyCompositionData,
    BodyCompositionDataResponse,
    MonthlyStatistics,
    create_body_composition_data_response,
)


def test_body_composition_data_response_uses_camel_case_aliases() -> None:
    response = create_body_composition_data_response(
        [BodyCompositionData(date="2026-05-31", weight=70.0, body_fat=20.0)],
        [
            MonthlyStatistics(
                date="2026-05",
                weight=70.0,
                body_fat=20.0,
                weight_change_rate=None,
            )
        ],
    )

    dumped = response.model_dump(by_alias=True)

    assert dumped == {
        "bodyCompositions": [
            {
                "date": "2026-05-31",
                "weight": 70.0,
                "bodyFat": 20.0,
            }
        ],
        "monthlyStatistics": [
            {
                "date": "2026-05",
                "weight": 70.0,
                "bodyFat": 20.0,
                "weightChangeRate": None,
            }
        ],
    }


def test_body_composition_data_response_forbids_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        BodyCompositionDataResponse.model_validate(
            {
                "bodyCompositions": [
                    {
                        "date": "2026-05-31",
                        "weight": 70.0,
                        "bodyFat": 20.0,
                        "unexpected": True,
                    }
                ],
                "monthlyStatistics": [],
            }
        )
