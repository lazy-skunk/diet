import re

import pytest

from diet.nutrition_optimizer.models import Constraint


def test_valid_constraint() -> None:
    constraint = Constraint(
        min_max="min",
        nutrient="protein",
        unit="amount",
        value=10,
    )

    assert constraint.min_max == "min"
    assert constraint.nutrient == "protein"
    assert constraint.unit == "amount"
    assert constraint.value == 10


def test_invalid_min_max() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Invalid Min/Max value: invalid_min_max."
            " Valid values are ['min', 'max']."
        ),
    ):
        Constraint(
            min_max="invalid_min_max",
            nutrient="protein",
            unit="amount",
            value=10,
        )


def test_invalid_nutritional_component() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Invalid nutrient: invalid_nutrient. Valid nutrients are"
            " ['energy', 'protein', 'fat', 'carbohydrates']."
        ),
    ):
        Constraint(
            min_max="min",
            nutrient="invalid_nutrient",
            unit="amount",
            value=10,
        )


def test_invalid_unit() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Invalid unit: invalid_unit."
            " Valid units are ['amount', 'energy', 'ratio']."
        ),
    ):
        Constraint(
            min_max="min",
            nutrient="protein",
            unit="invalid_unit",
            value=10,
        )


def test_negative_value() -> None:
    with pytest.raises(
        ValueError, match="Constraint value must be non-negative. Got -1."
    ):
        Constraint(
            min_max="min",
            nutrient="protein",
            unit="amount",
            value=-1,
        )


def test_zero_value() -> None:
    constraint = Constraint(
        min_max="min",
        nutrient="protein",
        unit="amount",
        value=0,
    )

    assert constraint.value == 0


def test_energy_constraint_must_use_energy_unit() -> None:
    with pytest.raises(
        ValueError, match="Energy constraints must use the energy unit."
    ):
        Constraint(
            min_max="min",
            nutrient="energy",
            unit="ratio",
            value=10,
        )


def test_macronutrient_constraint_must_not_use_energy_unit() -> None:
    with pytest.raises(
        ValueError,
        match="Macronutrient constraints must use amount or ratio units.",
    ):
        Constraint(
            min_max="min",
            nutrient="protein",
            unit="energy",
            value=10,
        )


def test_ratio_value_must_not_exceed_100() -> None:
    with pytest.raises(
        ValueError,
        match="Ratio constraint value must be between 0 and 100. Got 101.",
    ):
        Constraint(
            min_max="max",
            nutrient="protein",
            unit="ratio",
            value=101,
        )


def test_ratio_value_allows_100() -> None:
    constraint = Constraint(
        min_max="max",
        nutrient="protein",
        unit="ratio",
        value=100,
    )

    assert constraint.value == 100
