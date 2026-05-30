from dataclasses import dataclass
from logging import INFO, basicConfig, getLogger
from typing import Literal, cast

from pulp import (
    LpAffineExpression,
    LpMaximize,
    LpProblem,
    LpStatus,
    LpVariable,
)

basicConfig(level=INFO)
logger = getLogger(__name__)

NutritionKey = Literal["protein", "fat", "carbohydrate", "kcal"]


@dataclass
class VariableOptions:
    name: str
    lowBound: float
    upBound: float
    cat: str


@dataclass
class Food:
    name: str
    unit_label: str
    grams_per_unit: float
    nutrition_per_100g: dict[NutritionKey, float]
    variable_options: VariableOptions
    variable: LpVariable | None = None


GRAM_CALCULATION_FACTOR = 100
PROTEIN_KCAL_PER_GRAM = 4
FAT_KCAL_PER_GRAM = 9
CARBOHYDRATE_KCAL_PER_GRAM = 4

FOODS: dict[str, Food] = {
    "rice": Food(
        name="ご飯",
        unit_label="杯",
        grams_per_unit=200,
        nutrition_per_100g={
            "protein": 2.8,
            "fat": 1,
            "carbohydrate": 35.6,
            "kcal": 152,
        },
        variable_options=VariableOptions(
            name="米の量",
            lowBound=3,
            upBound=3,
            cat="Integer",
        ),
    ),
    "chicken_fillet": Food(
        name="ささみ",
        unit_label="つ",
        grams_per_unit=40,
        nutrition_per_100g={
            "protein": 29.6,
            "fat": 1,
            "carbohydrate": 0,
            "kcal": 121,
        },
        variable_options=VariableOptions(
            name="ささみの数",
            lowBound=6,
            upBound=6,
            cat="Integer",
        ),
    ),
    "boiled_egg": Food(
        name="ゆで卵",
        unit_label="つ",
        grams_per_unit=50,
        nutrition_per_100g={
            "protein": 12.5,
            "fat": 10.4,
            "carbohydrate": 0.3,
            "kcal": 134,
        },
        variable_options=VariableOptions(
            name="ゆで卵の数",
            lowBound=3,
            upBound=3,
            cat="Integer",
        ),
    ),
    "broccoli": Food(
        name="ブロッコリー",
        unit_label="つ",
        grams_per_unit=15,
        nutrition_per_100g={
            "protein": 3.9,
            "fat": 0.4,
            "carbohydrate": 5.2,
            "kcal": 30,
        },
        variable_options=VariableOptions(
            name="ブロッコリーの数",
            lowBound=9,
            upBound=12,
            cat="Integer",
        ),
    ),
    "natto": Food(
        name="納豆",
        unit_label="つ",
        grams_per_unit=50,
        nutrition_per_100g={
            "protein": 13.0,
            "fat": 7.4,
            "carbohydrate": 12.8,
            "kcal": 158,
        },
        variable_options=VariableOptions(
            name="納豆の数",
            lowBound=1,
            upBound=2,
            cat="Integer",
        ),
    ),
    "tofu": Food(
        name="豆腐",
        unit_label="つ",
        grams_per_unit=150,
        nutrition_per_100g={
            "protein": 5.3,
            "fat": 3.8,
            "carbohydrate": 2.0,
            "kcal": 63,
        },
        variable_options=VariableOptions(
            name="豆腐の数",
            lowBound=1,
            upBound=2,
            cat="Integer",
        ),
    ),
}


def calculate_total(
    nutrient_key: NutritionKey, use_solution_value: bool = False
) -> LpAffineExpression | float:
    total: LpAffineExpression | float = 0
    for food in FOODS.values():
        variable = cast(LpVariable, food.variable)
        amount: LpVariable | float = variable
        if use_solution_value:
            amount = cast(float, variable.varValue)

        total += (
            food.nutrition_per_100g[nutrient_key]
            * food.grams_per_unit
            * amount
            / GRAM_CALCULATION_FACTOR
        )

    return total


def setup_food_variables(problem: LpProblem) -> None:
    for food in FOODS.values():
        food.variable = problem.add_variable(
            name=food.variable_options.name,
            lowBound=food.variable_options.lowBound,
            upBound=food.variable_options.upBound,
            cat=food.variable_options.cat,
        )


def build_problem() -> LpProblem:
    problem = LpProblem("制約に基づきカロリーを最大化", sense=LpMaximize)
    setup_food_variables(problem)

    total_kcal = calculate_total("kcal")
    total_protein_grams = calculate_total("protein")
    total_fat_grams = calculate_total("fat")

    problem += total_kcal, "カロリーを最大化"
    problem += total_kcal <= 1765, "カロリーの上限"
    problem += total_protein_grams <= 160, "たんぱく質のグラム数上限"
    problem += total_protein_grams >= 120, "たんぱく質のグラム数下限"
    problem += total_fat_grams * 9 <= total_kcal * 0.2, "脂質の割合上限"

    return problem


def main() -> None:
    problem = build_problem()
    problem.solve()

    if LpStatus[problem.status] == "Optimal":
        logger.info("最適解が見つかりました。")

        logger.info("-----")
        logger.info("1 日の総摂取量は次のとおりです。")
        for food in FOODS.values():
            variable = cast(LpVariable, food.variable)
            logger.info(f"{food.name}: {variable.varValue} {food.unit_label}")

        total_protein_value = calculate_total(
            "protein", use_solution_value=True
        )
        total_fat_value = calculate_total("fat", use_solution_value=True)
        total_carbohydrate_value = calculate_total(
            "carbohydrate", use_solution_value=True
        )
        total_kcal_value = calculate_total("kcal", use_solution_value=True)

        logger.info("-----")
        logger.info(f"総たんぱく質: {total_protein_value:.1f} g")
        logger.info(f"総脂質: {total_fat_value:.1f} g")
        logger.info(f"総炭水化物: {total_carbohydrate_value:.1f} g")
        logger.info(f"総カロリー: {total_kcal_value:.1f} kcal")

        logger.info("-----")
        total_protein_kcal = total_protein_value * PROTEIN_KCAL_PER_GRAM
        total_fat_kcal = total_fat_value * FAT_KCAL_PER_GRAM
        total_carbohydrate_kcal = (
            total_carbohydrate_value * CARBOHYDRATE_KCAL_PER_GRAM
        )

        total_calories = (
            total_protein_kcal + total_fat_kcal + total_carbohydrate_kcal
        )
        protein_ratio = total_protein_kcal / total_calories * 100
        fat_ratio = total_fat_kcal / total_calories * 100
        carbohydrate_ratio = total_carbohydrate_kcal / total_calories * 100

        logger.info(f"たんぱく質割合: {round(protein_ratio, 1)}%")
        logger.info(f"脂質割合: {round(fat_ratio, 1)}%")
        logger.info(f"炭水化物割合: {round(carbohydrate_ratio, 1)}%")
    else:
        logger.info(
            "最適解が見つかりませんでした。制約条件を見直すと最適解が見つかる可能性があります。"
        )


if __name__ == "__main__":
    main()
