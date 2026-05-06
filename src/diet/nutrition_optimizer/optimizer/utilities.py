import re
from collections.abc import Callable, Mapping, Sequence

from flask import Request

from diet.nutrition_optimizer.optimizer.constraint import Constraint
from diet.nutrition_optimizer.optimizer.food_information import FoodInformation
from diet.nutrition_optimizer.optimizer.objective import Objective


def parse_request_data(
    request: Request,
) -> tuple[list[FoodInformation], Objective, list[Constraint]]:
    try:
        if request is None or request.json is None:
            raise ValueError("InvalidRequest")

        food_information_request = request.json.get("foodInformation")
        objective_request = request.json.get("objective")
        constraints_request = request.json.get("constraints")

        food_information = _convert_to_models(
            food_information_request, FoodInformation
        )
        objective = _convert_to_model(objective_request, Objective)
        constraints = _convert_to_models(constraints_request, Constraint)

        return food_information, objective, constraints
    except Exception as e:
        raise ValueError(f"Error processing request data: {e}") from e


def convert_top_level_keys_to_camel_case(
    response: Mapping[str, object],
) -> dict[str, object]:
    return {_snake_to_camel(key): value for key, value in response.items()}


def _camel_to_snake(camel_case_str: str) -> str:
    camel_to_snake_pattern = r"([a-z])([A-Z])"
    replacement_string = r"\1_\2"
    return re.sub(
        camel_to_snake_pattern, replacement_string, camel_case_str
    ).lower()


def _snake_to_camel(snake_case_str: str) -> str:
    words = snake_case_str.split("_")
    return "".join(
        word.capitalize() if word_count != 0 else word
        for word_count, word in enumerate(words)
    )


def _convert_to_models[T](
    data: Sequence[Mapping[str, object]], cls: Callable[..., T]
) -> list[T]:
    return [_convert_to_model(item, cls) for item in data]


def _convert_to_model[T](
    data: Mapping[str, object], cls: Callable[..., T]
) -> T:
    return cls(**{_camel_to_snake(key): value for key, value in data.items()})
