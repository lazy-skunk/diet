from typing import cast

import pytest

from diet.nutrition_optimizer.models import (
    Constraint,
    FailedNutritionOptimizerResult,
    FoodInformation,
    Objective,
    OptimalNutritionOptimizerResult,
)
from diet.nutrition_optimizer.service import NutritionOptimizer

_FOOD_INFORMATION = [
    FoodInformation(
        name="boiled_egg",
        energy=134,
        protein=12.5,
        fat=10.4,
        carbohydrates=0.3,
        grams_per_unit=50,
        minimum_intake=1,
        maximum_intake=3,
    ),
]

_OBJECTIVE = Objective(sense="maximize", nutrient="energy")

_CONSTRAINTS = [
    Constraint(
        min_max="max",
        nutrient="energy",
        unit="energy",
        value=200,
    ),
    Constraint(
        min_max="min",
        nutrient="fat",
        unit="ratio",
        value=20,
    ),
]

_INFEASIBLE_CONSTRAINTS = [
    Constraint(
        min_max="max",
        nutrient="energy",
        unit="energy",
        value=1,
    ),
]


def test_solve() -> None:
    optimizer = NutritionOptimizer(_FOOD_INFORMATION, _OBJECTIVE, _CONSTRAINTS)
    result = optimizer.solve()

    assert result["status"] == "Optimal"
    optimal_result = cast(OptimalNutritionOptimizerResult, result)

    assert optimal_result["food_intakes"]["boiled_egg"] == 2
    assert optimal_result["total_nutrient_values"]["energy"] == 134
    assert "fat" in optimal_result["pfc_ratio"]


def test_infeasible() -> None:
    optimizer = NutritionOptimizer(
        _FOOD_INFORMATION, _OBJECTIVE, _INFEASIBLE_CONSTRAINTS
    )
    result = optimizer.solve()

    assert result["status"] == "Infeasible"
    failed_result = cast(FailedNutritionOptimizerResult, result)

    assert (
        failed_result["message"] == "Please review the constraints,"
        " the grams per unit, or the intake values."
    )


def test_duplicate_food_names_are_rejected() -> None:
    duplicate_food_information = [
        _FOOD_INFORMATION[0],
        FoodInformation(
            name="boiled_egg",
            energy=120,
            protein=10,
            fat=8,
            carbohydrates=1,
            grams_per_unit=50,
            minimum_intake=0,
            maximum_intake=3,
        ),
    ]

    with pytest.raises(
        ValueError, match="Food names must be unique: boiled_egg."
    ):
        NutritionOptimizer(
            duplicate_food_information, _OBJECTIVE, _CONSTRAINTS
        )


def test_same_kind_constraints_do_not_conflict() -> None:
    constraints = [
        Constraint(
            min_max="max",
            nutrient="energy",
            unit="energy",
            value=200,
        ),
        Constraint(
            min_max="max",
            nutrient="energy",
            unit="energy",
            value=180,
        ),
    ]

    optimizer = NutritionOptimizer(_FOOD_INFORMATION, _OBJECTIVE, constraints)
    result = optimizer.solve()

    assert result["status"] == "Optimal"


def test_solve_with_multiple_foods_calculates_totals_by_food_name() -> None:
    food_information = [
        FoodInformation(
            name="boiled_egg",
            energy=134,
            protein=12.5,
            fat=10.4,
            carbohydrates=0.3,
            grams_per_unit=50,
            minimum_intake=2,
            maximum_intake=2,
        ),
        FoodInformation(
            name="rice",
            energy=156,
            protein=2.6,
            fat=0.4,
            carbohydrates=37.2,
            grams_per_unit=150,
            minimum_intake=1,
            maximum_intake=1,
        ),
    ]

    optimizer = NutritionOptimizer(food_information, _OBJECTIVE, [])
    result = optimizer.solve()

    assert result["status"] == "Optimal"
    optimal_result = cast(OptimalNutritionOptimizerResult, result)

    assert optimal_result["food_intakes"] == {"boiled_egg": 2, "rice": 1}
    assert optimal_result["total_nutrient_values"] == {
        "energy": 368.0,
        "protein": 16.4,
        "fat": 11.0,
        "carbohydrates": 56.1,
    }


def test_solve_returns_zero_pfc_ratio_when_macro_energy_is_zero() -> None:
    food_information = [
        FoodInformation(
            name="zero_macro_food",
            energy=100,
            protein=0,
            fat=0,
            carbohydrates=0,
            grams_per_unit=100,
            minimum_intake=1,
            maximum_intake=1,
        )
    ]

    optimizer = NutritionOptimizer(food_information, _OBJECTIVE, [])
    result = optimizer.solve()

    assert result["status"] == "Optimal"
    optimal_result = cast(OptimalNutritionOptimizerResult, result)

    assert optimal_result["pfc_ratio"] == {
        "protein": 0.0,
        "fat": 0.0,
        "carbohydrates": 0.0,
    }
