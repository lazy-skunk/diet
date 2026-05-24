from flask import Request
from pulp import (
    LpAffineExpression,
    LpInteger,
    LpMaximize,
    LpMinimize,
    LpProblem,
    LpStatus,
    LpVariable,
)

from diet.nutrition_optimizer.api_models import (
    OptimizeRequest,
    OptimizeResponse,
    validate_optimize_request,
)
from diet.nutrition_optimizer.models import (
    Constraint,
    FoodInformation,
    NutritionOptimizerResult,
    Objective,
)
from diet.utils.custom_logger import get_logger

_logger = get_logger()


class NutritionOptimizer:
    _GRAM_CALCULATION_FACTOR = 100

    def __init__(
        self,
        food_information: list[FoodInformation],
        objective: Objective,
        constraints: list[Constraint],
    ) -> None:
        self._food_information = food_information
        self._objective = objective
        self._constraints = constraints
        self._validate_food_names_are_unique()

        self._food_intake_variables: dict[str, LpVariable] = {}
        self._problem: LpProblem = self._create_lp_problem()
        self._objective_variables: dict[str, float | LpAffineExpression] = {
            nutrient: 0.0 for nutrient in FoodInformation.NUTRIENTS
        }

    def _validate_food_names_are_unique(self) -> None:
        food_names = [item.name for item in self._food_information]
        duplicate_food_names = {
            food_name
            for food_name in food_names
            if food_names.count(food_name) > 1
        }
        if duplicate_food_names:
            duplicate_names = ", ".join(sorted(duplicate_food_names))
            raise ValueError(f"Food names must be unique: {duplicate_names}.")

    def _setup_food_intake_variables(self) -> None:
        _logger.info("Setting up food intake variables.")

        for food_information in self._food_information:
            self._food_intake_variables[food_information.name] = (
                self._problem.add_variable(
                    food_information.name,
                    lowBound=food_information.minimum_intake,
                    upBound=food_information.maximum_intake,
                    cat=LpInteger,
                )
            )

        _logger.info("Completed setting up food intake variables.")

    def _get_objective_variable(
        self, nutrient: str
    ) -> float | LpAffineExpression:
        return self._objective_variables[nutrient]

    def _create_lp_problem(self) -> LpProblem:
        objective = (
            LpMaximize if self._objective.sense == "maximize" else LpMinimize
        )
        objective_name = f"{self._objective.sense}_{self._objective.nutrient}"

        return LpProblem(objective_name, objective)

    def _setup_objective(self) -> None:
        _logger.info("Setting up objective.")

        objective_name = f"{self._objective.sense}_{self._objective.nutrient}"
        self._problem += (
            self._get_objective_variable(self._objective.nutrient),
            objective_name,
        )

        _logger.info("Completed setting up objective.")

    def _update_objective_variable(
        self,
        nutrient: str,
        objective_variables: float | LpAffineExpression,
    ) -> None:
        self._objective_variables[nutrient] = objective_variables

    def _setup_objective_variables(self) -> None:
        _logger.info("Setting up objective variables.")

        for food_information in self._food_information:
            for nutrient in FoodInformation.NUTRIENTS:
                nutrient_value = getattr(food_information, nutrient)
                objective_variable = (
                    nutrient_value
                    * food_information.grams_per_unit
                    * self._food_intake_variables[food_information.name]
                    / self._GRAM_CALCULATION_FACTOR
                )

                current_objective_variables = self._get_objective_variable(
                    nutrient
                )
                self._update_objective_variable(
                    nutrient,
                    current_objective_variables + objective_variable,
                )

        _logger.info("Completed setting up objective variables.")

    def _apply_amount_or_energy_constraint(
        self, constraint: Constraint, constraint_index: int
    ) -> None:
        constraint_operations = {
            "max": lambda objective_variable, value: (
                objective_variable <= value
            ),
            "min": lambda objective_variable, value: (
                objective_variable >= value
            ),
        }

        constraint_name = (
            f"{constraint_index}_{constraint.min_max}_"
            f"{constraint.nutrient}_{constraint.unit}"
        )
        objective_variable = self._get_objective_variable(constraint.nutrient)

        self._problem += (
            constraint_operations[constraint.min_max](
                objective_variable, constraint.value
            ),
            constraint_name,
        )

    def _get_nutrient_energy_per_gram(self, nutrient: str) -> int:
        nutrient_energy_per_gram_attribute = (
            f"{nutrient.upper()}_ENERGY_PER_GRAM"
        )
        return getattr(FoodInformation, nutrient_energy_per_gram_attribute)

    def _apply_ratio_constraint(
        self, constraint: Constraint, constraint_index: int
    ) -> None:
        objective_variable = self._get_objective_variable(constraint.nutrient)
        total_energy = self._get_objective_variable("energy")
        nutrient_energy_per_gram = self._get_nutrient_energy_per_gram(
            constraint.nutrient
        )
        total_nutrient_energy = objective_variable * nutrient_energy_per_gram

        calculation_factor = constraint.value / self._GRAM_CALCULATION_FACTOR
        comparison_operations = {
            "max": lambda nutrient_energy: (
                nutrient_energy <= total_energy * calculation_factor
            ),
            "min": lambda nutrient_energy: (
                nutrient_energy >= total_energy * calculation_factor
            ),
        }

        self._problem += (
            comparison_operations[constraint.min_max](total_nutrient_energy),
            f"{constraint_index}_{constraint.min_max}_"
            f"{constraint.nutrient}_{constraint.unit}",
        )

    def _setup_constraints(self) -> None:
        _logger.info("Setting up constraints.")

        apply_methods = {
            "amount": self._apply_amount_or_energy_constraint,
            "energy": self._apply_amount_or_energy_constraint,
            "ratio": self._apply_ratio_constraint,
        }

        for constraint_index, constraint in enumerate(
            self._constraints, start=1
        ):
            apply_methods[constraint.unit](constraint, constraint_index)

        _logger.info("Completed setting up constraints.")

    def _get_food_intake_value(self, food_name: str) -> float:
        food_intake_value = self._food_intake_variables[food_name].varValue
        if food_intake_value is None:
            raise RuntimeError(f"Food intake value is missing: {food_name}.")

        return food_intake_value

    def _calculate_food_intakes(self) -> dict[str, float]:
        return {
            food_name: self._get_food_intake_value(food_name)
            for food_name in self._food_intake_variables
        }

    def _calculate_total_nutrient_values(self) -> dict[str, float]:
        total_nutrient_values: dict[str, float] = {}

        for nutrient in FoodInformation.NUTRIENTS:
            total_nutrient_value = sum(
                getattr(food_information, nutrient)
                * food_information.grams_per_unit
                * self._get_food_intake_value(food_information.name)
                / self._GRAM_CALCULATION_FACTOR
                for food_information in self._food_information
            )
            total_nutrient_values[nutrient] = round(total_nutrient_value, 1)

        return total_nutrient_values

    def _recalculate_total_energy(
        self, total_values: dict[str, float]
    ) -> float:
        recalculated_total_energy = 0.0

        for nutrient in FoodInformation.NUTRIENTS:
            if nutrient == "energy":
                continue

            energy_per_gram = self._get_nutrient_energy_per_gram(nutrient)
            recalculated_total_energy += (
                total_values[nutrient] * energy_per_gram
            )

        return recalculated_total_energy

    def _calculate_pfc_ratio(
        self, total_nutrient_values: dict[str, float]
    ) -> dict[str, float]:
        pfc_ratio: dict[str, float] = {}
        recalculated_total_energy = self._recalculate_total_energy(
            total_nutrient_values
        )
        if recalculated_total_energy == 0:
            _logger.warning(
                "Skipping PFC ratio calculation because total energy is zero."
            )
            return {
                nutrient_component: 0.0
                for nutrient_component in FoodInformation.NUTRIENTS
                if nutrient_component != "energy"
            }

        for nutrient_component in FoodInformation.NUTRIENTS:
            if nutrient_component == "energy":
                continue

            total_nutrient_value = total_nutrient_values[nutrient_component]
            energy_per_gram = self._get_nutrient_energy_per_gram(
                nutrient_component
            )
            ratio = (
                total_nutrient_value
                * energy_per_gram
                / recalculated_total_energy
            ) * self._GRAM_CALCULATION_FACTOR
            pfc_ratio[nutrient_component] = round(ratio, 1)

        return pfc_ratio

    def _preparation(self) -> None:
        _logger.info("Starting preparation for solve.")

        self._setup_food_intake_variables()
        self._setup_objective_variables()
        self._setup_objective()
        self._setup_constraints()

        _logger.info("Completed preparation for solve.")

    def solve(self) -> NutritionOptimizerResult:
        self._preparation()

        _logger.info("Starting to solve the optimization problem.")
        self._problem.solve()

        solution_result = LpStatus[self._problem.status]
        if solution_result == "Optimal":
            _logger.info("Optimization completed successfully.")

            food_intakes = self._calculate_food_intakes()
            total_nutrient_values = self._calculate_total_nutrient_values()
            pfc_ratio = self._calculate_pfc_ratio(total_nutrient_values)

            return {
                "status": solution_result,
                "food_intakes": food_intakes,
                "total_nutrient_values": total_nutrient_values,
                "pfc_ratio": pfc_ratio,
            }

        _logger.warning(f"Optimization failed with status: {solution_result}")
        return {
            "status": solution_result,
            "message": "Please review the constraints,"
            " the grams per unit, or the intake values.",
        }


def optimize(request: Request) -> dict[str, object]:
    _logger.info("Start: optimize nutrition request")

    optimize_request = _parse_optimize_request(request)
    food_information, objective, constraints = optimize_request.to_domain()
    nutrition_optimizer = NutritionOptimizer(
        food_information, objective, constraints
    )
    result = nutrition_optimizer.solve()
    parsed_result = OptimizeResponse.from_domain_result(result).model_dump(
        by_alias=True
    )

    _logger.info("End: optimize nutrition request")
    return parsed_result


def _parse_optimize_request(request: Request) -> OptimizeRequest:
    payload = request.get_json(silent=True)
    if payload is None:
        raise ValueError("Invalid request data: request JSON is required")

    return validate_optimize_request(payload)
