from pytest_mock import MockerFixture

from diet.nutrition_optimizer.service import optimize


def test_optimize(mocker: MockerFixture) -> None:
    food_information = mocker.sentinel.food_information
    objective = mocker.sentinel.objective
    constraints = mocker.sentinel.constraints
    domain_result = {"status": "Optimal", "food_intake_grams": {"egg": 2}}
    mock_optimizer = mocker.Mock()
    mock_optimizer.solve.return_value = domain_result
    mock_optimizer_class = mocker.patch(
        "diet.nutrition_optimizer.service.NutritionOptimizer",
        return_value=mock_optimizer,
    )

    result = optimize(food_information, objective, constraints)

    assert result == domain_result
    mock_optimizer_class.assert_called_once_with(
        food_information, objective, constraints
    )
    mock_optimizer.solve.assert_called_once_with()
