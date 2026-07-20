import pytest

from diet.nutrition_optimizer.models import FoodInformation


def test_valid_food_information() -> None:
    boiled_egg = FoodInformation(
        name="boiled_egg",
        energy=134,
        protein=12.5,
        fat=10.4,
        carbohydrates=0.3,
        minimum_intake_grams=50,
        maximum_intake_grams=150,
    )

    assert boiled_egg.name == "boiled_egg"
    assert boiled_egg.energy == 134
    assert boiled_egg.protein == 12.5
    assert boiled_egg.fat == 10.4
    assert boiled_egg.carbohydrates == 0.3
    assert boiled_egg.minimum_intake_grams == 50
    assert boiled_egg.maximum_intake_grams == 150


def test_blank_name() -> None:
    with pytest.raises(ValueError, match="Food name must be provided."):
        FoodInformation(
            name=" ",
            energy=134,
            protein=12.5,
            fat=10.4,
            carbohydrates=0.3,
            minimum_intake_grams=50,
            maximum_intake_grams=150,
        )


def test_negative_nutrient_values() -> None:
    nutrients = ["energy", "protein", "fat", "carbohydrates"]
    for nutrient in nutrients:
        with pytest.raises(
            ValueError,
            match="Invalid values for boiled_egg."
            " All nutrient values must be finite and non-negative.",
        ):
            FoodInformation(
                name="boiled_egg",
                energy=-134 if nutrient == "energy" else 134,
                protein=-12.5 if nutrient == "protein" else 12.5,
                fat=-10.4 if nutrient == "fat" else 10.4,
                carbohydrates=-0.3 if nutrient == "carbohydrates" else 0.3,
                minimum_intake_grams=50,
                maximum_intake_grams=150,
            )


@pytest.mark.parametrize(
    "invalid_value",
    [float("nan"), float("inf"), float("-inf")],
)
def test_non_finite_nutrient_values(invalid_value: float) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Invalid values for boiled_egg."
            " All nutrient values must be finite and non-negative."
        ),
    ):
        FoodInformation(
            name="boiled_egg",
            energy=invalid_value,
            protein=12.5,
            fat=10.4,
            carbohydrates=0.3,
            minimum_intake_grams=50,
            maximum_intake_grams=150,
        )


def test_negative_intake_grams_values() -> None:
    negative_intake_grams_values = [
        (-1, 3),
        (1, -3),
    ]

    for (
        minimum_intake_grams,
        maximum_intake_grams,
    ) in negative_intake_grams_values:
        with pytest.raises(
            ValueError,
            match=(
                "Both minimum_intake_grams and maximum_intake_grams"
                " must be non-negative."
            ),
        ):
            FoodInformation(
                name="boiled_egg",
                energy=134,
                protein=12.5,
                fat=10.4,
                carbohydrates=0.3,
                minimum_intake_grams=minimum_intake_grams,
                maximum_intake_grams=maximum_intake_grams,
            )


def test_minimum_intake_grams_is_less_than_maximum_intake_grams() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Maximum_intake_grams must be greater than minimum_intake_grams."
        ),
    ):
        FoodInformation(
            name="boiled_egg",
            energy=134,
            protein=12.5,
            fat=10.4,
            carbohydrates=0.3,
            minimum_intake_grams=3,
            maximum_intake_grams=1,
        )
