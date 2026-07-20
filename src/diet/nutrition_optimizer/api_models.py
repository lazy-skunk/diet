from typing import Literal, Self

from pydantic import (
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from diet.api_models import ApiModel
from diet.nutrition_optimizer.models import (
    Constraint,
    FoodInformation,
    NutritionOptimizerResult,
    Objective,
)


class FoodSelectionInput(ApiModel):
    food_name: str
    energy: float
    protein: float
    fat: float
    carbohydrates: float
    minimum_intake_grams: int
    maximum_intake_grams: int

    @field_validator("food_name")
    @classmethod
    def normalize_food_name(cls, food_name: str) -> str:
        normalized_name = food_name.strip()
        if not normalized_name:
            raise ValueError("Food name must be provided.")
        return normalized_name

    def to_domain(self) -> FoodInformation:
        return FoodInformation(
            name=self.food_name,
            energy=self.energy,
            protein=self.protein,
            fat=self.fat,
            carbohydrates=self.carbohydrates,
            minimum_intake_grams=self.minimum_intake_grams,
            maximum_intake_grams=self.maximum_intake_grams,
        )


class ObjectiveInput(ApiModel):
    sense: str
    nutrient: str

    def to_domain(self) -> Objective:
        return Objective(**self.model_dump())


class ConstraintInput(ApiModel):
    min_max: str
    nutrient: str
    unit: str
    value: float

    def to_domain(self) -> Constraint:
        return Constraint(**self.model_dump())


class OptimizeRequest(ApiModel):
    food_selections: list[FoodSelectionInput] = Field(min_length=1)
    objective: ObjectiveInput
    constraints: list[ConstraintInput]

    @field_validator("food_selections")
    @classmethod
    def validate_food_names_are_unique(
        cls, food_selections: list[FoodSelectionInput]
    ) -> list[FoodSelectionInput]:
        food_names = [selection.food_name for selection in food_selections]
        if len(food_names) != len(set(food_names)):
            raise ValueError("Food names must be unique.")
        return food_selections

    def to_domain(
        self,
    ) -> tuple[list[FoodInformation], Objective, list[Constraint]]:
        return (
            [item.to_domain() for item in self.food_selections],
            self.objective.to_domain(),
            [item.to_domain() for item in self.constraints],
        )


class OptimizeResponse(ApiModel):
    status: str
    food_intake_grams: dict[str, int] | None = None
    total_nutrient_values: dict[str, float] | None = None
    pfc_composition_ratio: dict[str, float] | None = None
    error_code: str | None = None

    @model_validator(mode="after")
    def validate_result_matches_status(self) -> Self:
        result_values = (
            self.food_intake_grams,
            self.total_nutrient_values,
            self.pfc_composition_ratio,
        )

        if self.status == "Optimal":
            if any(value is None for value in result_values):
                raise ValueError(
                    "An optimal response must include all result values."
                )
            if self.error_code is not None:
                raise ValueError(
                    "An optimal response must not include an error code."
                )
            return self

        if self.error_code is None:
            raise ValueError("A failed response must include an error code.")
        if any(value is not None for value in result_values):
            raise ValueError(
                "A failed response must not include result values."
            )
        return self

    @classmethod
    def from_domain_result(
        cls, result: NutritionOptimizerResult
    ) -> "OptimizeResponse":
        return cls.model_validate(result)


ErrorCode = Literal[
    "request_verification_failed",
    "invalid_input",
    "unexpected_response",
]


class ErrorResponse(ApiModel):
    status: Literal["Error"] = "Error"
    error_code: ErrorCode


def validate_optimize_request(payload: object) -> OptimizeRequest:
    try:
        return OptimizeRequest.model_validate(payload)
    except ValidationError as e:
        raise ValueError(_format_validation_error(e)) from e


def _format_validation_error(error: ValidationError) -> str:
    error_details = []
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"])
        error_details.append(f"{location}: {item['msg']}")

    return "Invalid request data: " + "; ".join(error_details)
