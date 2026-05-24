from pydantic import BaseModel, ConfigDict, Field, ValidationError

from diet.nutrition_optimizer.models import (
    Constraint,
    FoodInformation,
    NutritionOptimizerResult,
    Objective,
)


def _to_camel(snake_case_str: str) -> str:
    words = snake_case_str.split("_")
    return "".join(
        word.capitalize() if index != 0 else word
        for index, word in enumerate(words)
    )


class NutritionOptimizerApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
        loc_by_alias=False,
        extra="forbid",
    )


class FoodInformationInput(NutritionOptimizerApiModel):
    name: str
    energy: float
    protein: float
    fat: float
    carbohydrates: float
    grams_per_unit: int
    minimum_intake: int
    maximum_intake: int

    def to_domain(self) -> FoodInformation:
        return FoodInformation(**self.model_dump())


class ObjectiveInput(NutritionOptimizerApiModel):
    sense: str
    nutrient: str

    def to_domain(self) -> Objective:
        return Objective(**self.model_dump())


class ConstraintInput(NutritionOptimizerApiModel):
    min_max: str
    nutrient: str
    unit: str
    value: float

    def to_domain(self) -> Constraint:
        return Constraint(**self.model_dump())


class OptimizeRequest(NutritionOptimizerApiModel):
    food_information: list[FoodInformationInput] = Field(min_length=1)
    objective: ObjectiveInput
    constraints: list[ConstraintInput]

    def to_domain(
        self,
    ) -> tuple[list[FoodInformation], Objective, list[Constraint]]:
        return (
            [item.to_domain() for item in self.food_information],
            self.objective.to_domain(),
            [item.to_domain() for item in self.constraints],
        )


class OptimizeResponse(NutritionOptimizerApiModel):
    status: str
    food_intakes: dict[str, float] | None = None
    total_nutrient_values: dict[str, float] | None = None
    pfc_ratio: dict[str, float] | None = None
    message: str | None = None

    @classmethod
    def from_domain_result(
        cls, result: NutritionOptimizerResult
    ) -> "OptimizeResponse":
        return cls.model_validate(result)


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
