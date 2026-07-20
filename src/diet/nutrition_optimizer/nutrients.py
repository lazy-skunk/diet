from dataclasses import dataclass

NUTRIENT_REFERENCE_GRAMS = 100


@dataclass(frozen=True)
class NutrientDefinition:
    key: str
    food_master_identifier: str
    unit: str
    translation_key: str
    energy_per_gram: int | None


NUTRIENTS = (
    NutrientDefinition(
        key="energy",
        food_master_identifier="ENERC_KCAL",
        unit="kcal",
        translation_key="nutrition.energy",
        energy_per_gram=None,
    ),
    NutrientDefinition(
        key="protein",
        food_master_identifier="PROT-",
        unit="g",
        translation_key="nutrition.protein",
        energy_per_gram=4,
    ),
    NutrientDefinition(
        key="fat",
        food_master_identifier="FAT-",
        unit="g",
        translation_key="nutrition.fat",
        energy_per_gram=9,
    ),
    NutrientDefinition(
        key="carbohydrates",
        food_master_identifier="CHOCDF-",
        unit="g",
        translation_key="nutrition.carbohydrates",
        energy_per_gram=4,
    ),
)

NUTRIENTS_BY_KEY = {nutrient.key: nutrient for nutrient in NUTRIENTS}
NUTRIENT_KEYS = tuple(nutrient.key for nutrient in NUTRIENTS)
