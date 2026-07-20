from pulp import (
    LpAffineExpression,
    LpInteger,
    LpMaximize,
    LpMinimize,
    LpProblem,
    LpStatus,
    LpVariable,
)

from diet.nutrition_optimizer.models import (
    Constraint,
    FoodInformation,
    NutritionOptimizerResult,
    Objective,
)
from diet.nutrition_optimizer.nutrients import (
    NUTRIENT_KEYS,
    NUTRIENT_REFERENCE_GRAMS,
    NUTRIENTS_BY_KEY,
)
from diet.utils.custom_logger import get_logger

_logger = get_logger()


class NutritionOptimizer:
    _PERCENTAGE_FACTOR = 100
    _PFC_ENERGY_EPSILON = 1e-6

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

        self._food_intake_grams_variables: dict[str, LpVariable] = {}
        self._problem: LpProblem = self._create_lp_problem()
        self._objective_variables: dict[str, float | LpAffineExpression] = {
            nutrient: 0.0 for nutrient in NUTRIENT_KEYS
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

    def _setup_food_intake_grams_variables(self) -> None:
        _logger.info("Setting up food intake gram variables.")

        for food_information in self._food_information:
            self._food_intake_grams_variables[food_information.name] = (
                self._problem.add_variable(
                    food_information.name,
                    lowBound=food_information.minimum_intake_grams,
                    upBound=food_information.maximum_intake_grams,
                    cat=LpInteger,
                )
            )

        _logger.info("Completed setting up food intake gram variables.")

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
            for nutrient in NUTRIENT_KEYS:
                nutrient_value = getattr(food_information, nutrient)
                objective_variable = (
                    nutrient_value
                    * self._food_intake_grams_variables[food_information.name]
                    / NUTRIENT_REFERENCE_GRAMS
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
        energy_per_gram = NUTRIENTS_BY_KEY[nutrient].energy_per_gram
        if energy_per_gram is None:
            raise RuntimeError(
                f"Nutrient has no energy conversion factor: {nutrient}."
            )
        return energy_per_gram

    def _calculate_pfc_energy(
        self,
    ) -> float | LpAffineExpression:
        pfc_energy: float | LpAffineExpression = 0.0
        for nutrient in NUTRIENT_KEYS:
            if nutrient == "energy":
                continue
            pfc_energy += self._get_objective_variable(
                nutrient
            ) * self._get_nutrient_energy_per_gram(nutrient)
        return pfc_energy

    def _apply_pfc_ratio_constraint(
        self, constraint: Constraint, constraint_index: int
    ) -> None:
        objective_variable = self._get_objective_variable(constraint.nutrient)
        pfc_energy = self._calculate_pfc_energy()
        nutrient_energy_per_gram = self._get_nutrient_energy_per_gram(
            constraint.nutrient
        )
        total_nutrient_energy = objective_variable * nutrient_energy_per_gram

        calculation_factor = constraint.value / self._PERCENTAGE_FACTOR
        comparison_operations = {
            "max": lambda nutrient_energy: (
                nutrient_energy <= pfc_energy * calculation_factor
            ),
            "min": lambda nutrient_energy: (
                nutrient_energy >= pfc_energy * calculation_factor
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
            "pfc_ratio": self._apply_pfc_ratio_constraint,
        }

        if any(
            constraint.unit == "pfc_ratio" for constraint in self._constraints
        ):
            self._problem += (
                self._calculate_pfc_energy() >= self._PFC_ENERGY_EPSILON,
                "pfc_energy_must_be_positive",
            )

        for constraint_index, constraint in enumerate(
            self._constraints, start=1
        ):
            apply_methods[constraint.unit](constraint, constraint_index)

        _logger.info("Completed setting up constraints.")

    def _get_food_intake_grams(self, food_information: FoodInformation) -> int:
        food_intake_grams = self._food_intake_grams_variables[
            food_information.name
        ].varValue
        if food_intake_grams is None:
            return food_information.minimum_intake_grams

        return int(round(food_intake_grams))

    def _calculate_food_intake_grams(self) -> dict[str, int]:
        return {
            food_information.name: self._get_food_intake_grams(
                food_information
            )
            for food_information in self._food_information
        }

    def _calculate_total_nutrient_value(self, nutrient: str) -> float:
        return sum(
            getattr(food_information, nutrient)
            * self._get_food_intake_grams(food_information)
            / NUTRIENT_REFERENCE_GRAMS
            for food_information in self._food_information
        )

    def _calculate_total_nutrient_values(self) -> dict[str, float]:
        return {
            nutrient: round(self._calculate_total_nutrient_value(nutrient), 1)
            for nutrient in NUTRIENT_KEYS
        }

    def _calculate_pfc_composition_ratio(self) -> dict[str, float]:
        pfc_energy = sum(
            self._calculate_total_nutrient_value(nutrient)
            * self._get_nutrient_energy_per_gram(nutrient)
            for nutrient in NUTRIENT_KEYS
            if nutrient != "energy"
        )
        if pfc_energy == 0:
            _logger.warning(
                "Skipping PFC composition ratio calculation because "
                "PFC energy is zero."
            )
            return {
                nutrient: 0.0
                for nutrient in NUTRIENT_KEYS
                if nutrient != "energy"
            }

        return {
            nutrient: round(
                self._calculate_total_nutrient_value(nutrient)
                * self._get_nutrient_energy_per_gram(nutrient)
                / pfc_energy
                * self._PERCENTAGE_FACTOR,
                1,
            )
            for nutrient in NUTRIENT_KEYS
            if nutrient != "energy"
        }

    def _preparation(self) -> None:
        _logger.info("Starting preparation for solve.")

        self._setup_food_intake_grams_variables()
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

            food_intake_grams = self._calculate_food_intake_grams()
            total_nutrient_values = self._calculate_total_nutrient_values()
            pfc_composition_ratio = self._calculate_pfc_composition_ratio()

            return {
                "status": solution_result,
                "food_intake_grams": food_intake_grams,
                "total_nutrient_values": total_nutrient_values,
                "pfc_composition_ratio": pfc_composition_ratio,
            }

        _logger.warning(f"Optimization failed with status: {solution_result}")
        error_code = (
            "optimization_infeasible"
            if solution_result == "Infeasible"
            else "optimization_failed"
        )
        return {
            "status": solution_result,
            "error_code": error_code,
        }
