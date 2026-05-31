from dataclasses import dataclass
from typing import ClassVar, Literal, TypedDict


class OptimalNutritionOptimizerResult(TypedDict):
    status: Literal["Optimal"]
    food_intakes: dict[str, float]
    total_nutrient_values: dict[str, float]
    pfc_ratio: dict[str, float]


class FailedNutritionOptimizerResult(TypedDict):
    status: str
    message: str


NutritionOptimizerResult = (
    OptimalNutritionOptimizerResult | FailedNutritionOptimizerResult
)


@dataclass(frozen=True)
class FoodInformation:
    name: str
    energy: float
    protein: float
    fat: float
    carbohydrates: float
    grams_per_unit: int
    minimum_intake: int
    maximum_intake: int

    PROTEIN_ENERGY_PER_GRAM: ClassVar[int] = 4
    FAT_ENERGY_PER_GRAM: ClassVar[int] = 9
    CARBOHYDRATES_ENERGY_PER_GRAM: ClassVar[int] = 4
    NUTRIENTS: ClassVar[tuple[str, ...]] = (
        "energy",
        "protein",
        "fat",
        "carbohydrates",
    )

    def __post_init__(self) -> None:
        self._validate_name_is_not_blank()
        self._validate_nutrient_values_are_non_negative()
        self._validate_grams_per_unit_is_greater_than_zero()
        self._validate_intake_values_are_non_negative()
        self._validate_minimum_intake_is_less_than_maximum_intake()

    def _validate_name_is_not_blank(self) -> None:
        if not self.name.strip():
            raise ValueError("Food name must be provided.")

    def _validate_nutrient_values_are_non_negative(self) -> None:
        if any(
            value is None or value < 0
            for value in [
                self.energy,
                self.protein,
                self.fat,
                self.carbohydrates,
            ]
        ):
            raise ValueError(
                f"Invalid values for {self.name}."
                " All nutrient values must be non-negative."
            )

    def _validate_grams_per_unit_is_greater_than_zero(self) -> None:
        if self.grams_per_unit is None or self.grams_per_unit <= 0:
            raise ValueError(
                f"Invalid grams per unit for {self.name}."
                " It must be greater than zero."
            )

    def _validate_intake_values_are_non_negative(self) -> None:
        if any(
            value is None or value < 0
            for value in [self.minimum_intake, self.maximum_intake]
        ):
            raise ValueError(
                f"Invalid intake values for {self.name}."
                " Both minimum_intake and maximum_intake must be non-negative."
            )

    def _validate_minimum_intake_is_less_than_maximum_intake(self) -> None:
        if self.minimum_intake > self.maximum_intake:
            raise ValueError(
                f"Invalid intake range for {self.name}."
                " Maximum_intake must be greater than minimum_intake."
            )


@dataclass(frozen=True)
class Constraint:
    min_max: str
    nutrient: str
    unit: str
    value: float

    MIN_MAX: ClassVar[tuple[str, ...]] = ("min", "max")
    UNITS: ClassVar[tuple[str, ...]] = (
        "amount",
        "energy",
        "ratio",
    )

    def __post_init__(self) -> None:
        self._validate_min_max()
        self._validate_nutrient()
        self._validate_unit()
        self._validate_nutrient_unit_combination()
        self._validate_value_is_non_negative()
        self._validate_ratio_value_range()

    def _validate_min_max(self) -> None:
        if self.min_max not in self.MIN_MAX:
            raise ValueError(
                f"Invalid Min/Max value: {self.min_max}."
                f" Valid values are {list(Constraint.MIN_MAX)}."
            )

    def _validate_nutrient(self) -> None:
        if self.nutrient not in FoodInformation.NUTRIENTS:
            raise ValueError(
                f"Invalid nutrient: {self.nutrient}."
                f" Valid nutrients are {list(FoodInformation.NUTRIENTS)}."
            )

    def _validate_unit(self) -> None:
        if self.unit not in self.UNITS:
            raise ValueError(
                f"Invalid unit: {self.unit}."
                f" Valid units are {list(Constraint.UNITS)}."
            )

    def _validate_nutrient_unit_combination(self) -> None:
        if self.nutrient == "energy" and self.unit != "energy":
            raise ValueError("Energy constraints must use the energy unit.")

        if self.nutrient != "energy" and self.unit == "energy":
            raise ValueError(
                "Macronutrient constraints must use amount or ratio units."
            )

    def _validate_value_is_non_negative(self) -> None:
        if self.value is None or self.value < 0:
            raise ValueError(
                f"Constraint value must be non-negative. Got {self.value}."
            )

    def _validate_ratio_value_range(self) -> None:
        if self.unit == "ratio" and self.value > 100:
            raise ValueError(
                f"Ratio constraint value must be between 0 and 100."
                f" Got {self.value}."
            )


@dataclass(frozen=True)
class Objective:
    sense: str
    nutrient: str

    SENSES: ClassVar[tuple[str, ...]] = (
        "minimize",
        "maximize",
    )

    def __post_init__(self) -> None:
        self._validate_sense()
        self._validate_nutrient()

    def _validate_sense(self) -> None:
        if self.sense not in self.SENSES:
            raise ValueError(
                f"Invalid sense: {self.sense}."
                f" Valid values are {list(self.SENSES)}."
            )

    def _validate_nutrient(self) -> None:
        if self.nutrient not in FoodInformation.NUTRIENTS:
            raise ValueError(
                f"Invalid nutrient: {self.nutrient}."
                f" Valid nutrients are {list(FoodInformation.NUTRIENTS)}."
            )
