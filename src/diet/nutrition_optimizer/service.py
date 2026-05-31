from diet.nutrition_optimizer.models import (
    Constraint,
    FoodInformation,
    NutritionOptimizerResult,
    Objective,
)
from diet.nutrition_optimizer.optimizer import NutritionOptimizer
from diet.utils.custom_logger import get_logger

_logger = get_logger()


def optimize(
    food_information: list[FoodInformation],
    objective: Objective,
    constraints: list[Constraint],
) -> NutritionOptimizerResult:
    _logger.info("Start: optimize nutrition")

    nutrition_optimizer = NutritionOptimizer(
        food_information, objective, constraints
    )
    result = nutrition_optimizer.solve()

    _logger.info("End: optimize nutrition")
    return result
