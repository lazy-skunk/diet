from diet.nutrition_optimizer.nutrients import (
    NUTRIENT_KEYS,
    NUTRIENT_REFERENCE_GRAMS,
    NUTRIENTS,
    NUTRIENTS_BY_KEY,
)


def test_nutrient_indexes_are_derived_from_definitions() -> None:
    assert NUTRIENT_REFERENCE_GRAMS == 100
    assert tuple(nutrient.key for nutrient in NUTRIENTS) == NUTRIENT_KEYS
    assert NUTRIENTS_BY_KEY["protein"].food_master_identifier == "PROT-"


def test_macronutrient_energy_conversion_factors() -> None:
    assert NUTRIENTS_BY_KEY["energy"].energy_per_gram is None
    assert NUTRIENTS_BY_KEY["protein"].energy_per_gram == 4
    assert NUTRIENTS_BY_KEY["fat"].energy_per_gram == 9
    assert NUTRIENTS_BY_KEY["carbohydrates"].energy_per_gram == 4
