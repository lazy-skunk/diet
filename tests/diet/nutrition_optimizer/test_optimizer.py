from typing import cast

import pytest

from diet.nutrition_optimizer.models import (
    Constraint,
    FailedNutritionOptimizerResult,
    FoodInformation,
    Objective,
    OptimalNutritionOptimizerResult,
)
from diet.nutrition_optimizer.optimizer import NutritionOptimizer

_FOOD_INFORMATION = [
    FoodInformation(
        name="boiled_egg",
        energy=134,
        protein=12.5,
        fat=10.4,
        carbohydrates=0.3,
        minimum_intake_grams=50,
        maximum_intake_grams=150,
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
        unit="pfc_ratio",
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

    assert optimal_result["food_intake_grams"]["boiled_egg"] == 149
    assert isinstance(optimal_result["food_intake_grams"]["boiled_egg"], int)
    assert optimal_result["total_nutrient_values"]["energy"] == 199.7
    assert optimal_result["pfc_composition_ratio"] == {
        "protein": 34.5,
        "fat": 64.6,
        "carbohydrates": 0.8,
    }


def test_infeasible() -> None:
    optimizer = NutritionOptimizer(
        _FOOD_INFORMATION, _OBJECTIVE, _INFEASIBLE_CONSTRAINTS
    )
    result = optimizer.solve()

    assert result["status"] == "Infeasible"
    failed_result = cast(FailedNutritionOptimizerResult, result)

    assert failed_result["error_code"] == "optimization_infeasible"


def test_duplicate_food_names_are_rejected() -> None:
    duplicate_food_information = [
        _FOOD_INFORMATION[0],
        FoodInformation(
            name="boiled_egg",
            energy=120,
            protein=10,
            fat=8,
            carbohydrates=1,
            minimum_intake_grams=0,
            maximum_intake_grams=150,
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


def test_pfc_ratio_constraint_uses_pfc_energy_as_denominator() -> None:
    food_information = [
        FoodInformation(
            name="food_with_non_pfc_energy",
            energy=200,
            protein=10,
            fat=10,
            carbohydrates=10,
            minimum_intake_grams=100,
            maximum_intake_grams=100,
        )
    ]
    constraints = [
        Constraint(
            min_max="min",
            nutrient="fat",
            unit="pfc_ratio",
            value=50,
        )
    ]

    result = NutritionOptimizer(
        food_information, _OBJECTIVE, constraints
    ).solve()

    assert result["status"] == "Optimal"
    optimal_result = cast(OptimalNutritionOptimizerResult, result)
    assert optimal_result["pfc_composition_ratio"]["fat"] == 52.9


def test_pfc_ratio_constraint_rejects_zero_pfc_energy() -> None:
    food_information = [
        FoodInformation(
            name="distilled_spirit",
            energy=234,
            protein=0,
            fat=0,
            carbohydrates=0,
            minimum_intake_grams=0,
            maximum_intake_grams=300,
        )
    ]
    constraints = [
        Constraint(
            min_max="min",
            nutrient="protein",
            unit="pfc_ratio",
            value=20,
        )
    ]

    result = NutritionOptimizer(
        food_information, _OBJECTIVE, constraints
    ).solve()

    assert result["status"] == "Infeasible"


def test_solve_with_multiple_foods_calculates_totals_by_food_name() -> None:
    food_information = [
        FoodInformation(
            name="boiled_egg",
            energy=134,
            protein=12.5,
            fat=10.4,
            carbohydrates=0.3,
            minimum_intake_grams=100,
            maximum_intake_grams=100,
        ),
        FoodInformation(
            name="rice",
            energy=156,
            protein=2.6,
            fat=0.4,
            carbohydrates=37.2,
            minimum_intake_grams=150,
            maximum_intake_grams=150,
        ),
    ]

    optimizer = NutritionOptimizer(food_information, _OBJECTIVE, [])
    result = optimizer.solve()

    assert result["status"] == "Optimal"
    optimal_result = cast(OptimalNutritionOptimizerResult, result)

    assert optimal_result["food_intake_grams"] == {
        "boiled_egg": 100,
        "rice": 150,
    }
    assert optimal_result["total_nutrient_values"] == {
        "energy": 368.0,
        "protein": 16.4,
        "fat": 11.0,
        "carbohydrates": 56.1,
    }


def test_zero_pfc_energy_returns_zero_composition_ratios() -> None:
    food_information = [
        FoodInformation(
            name="zero_macro_food",
            energy=100,
            protein=0,
            fat=0,
            carbohydrates=0,
            minimum_intake_grams=100,
            maximum_intake_grams=100,
        )
    ]

    optimizer = NutritionOptimizer(food_information, _OBJECTIVE, [])
    result = optimizer.solve()

    assert result["status"] == "Optimal"
    optimal_result = cast(OptimalNutritionOptimizerResult, result)

    assert optimal_result["pfc_composition_ratio"] == {
        "protein": 0.0,
        "fat": 0.0,
        "carbohydrates": 0.0,
    }


def test_unused_optional_food_defaults_to_zero_intake_grams() -> None:
    food_information = [
        FoodInformation(
            name="optional_zero_nutrient_food",
            energy=0,
            protein=0,
            fat=0,
            carbohydrates=0,
            minimum_intake_grams=0,
            maximum_intake_grams=300,
        )
    ]

    result = NutritionOptimizer(food_information, _OBJECTIVE, []).solve()

    assert result["status"] == "Optimal"
    optimal_result = cast(OptimalNutritionOptimizerResult, result)
    assert optimal_result["food_intake_grams"] == {
        "optional_zero_nutrient_food": 0
    }
