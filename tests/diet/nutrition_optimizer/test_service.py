from pytest_mock import MockerFixture

from diet.nutrition_optimizer.service import optimize


def test_optimize(mocker: MockerFixture) -> None:
    payload = {"foodInformation": []}
    mock_optimize_request = mocker.Mock()
    food_information = mocker.sentinel.food_information
    objective = mocker.sentinel.objective
    constraints = mocker.sentinel.constraints
    mock_optimize_request.to_domain.return_value = (
        food_information,
        objective,
        constraints,
    )

    mocker.patch(
        "diet.nutrition_optimizer.service._parse_optimize_request",
        return_value=mock_optimize_request,
    )
    mock_optimizer = mocker.Mock()
    mock_optimizer.solve.return_value = {"food_intakes": {"egg": 2}}
    mock_optimizer_class = mocker.patch(
        "diet.nutrition_optimizer.service.NutritionOptimizer",
        return_value=mock_optimizer,
    )
    mock_response = mocker.Mock()
    mock_response.model_dump.return_value = {"foodIntakes": {"egg": 2}}
    mock_response_class = mocker.patch(
        "diet.nutrition_optimizer.service.OptimizeResponse.from_domain_result",
        return_value=mock_response,
    )

    result = optimize(payload)

    assert result == {"foodIntakes": {"egg": 2}}
    mock_optimizer_class.assert_called_once_with(
        food_information, objective, constraints
    )
    mock_optimizer.solve.assert_called_once_with()
    mock_response_class.assert_called_once_with({"food_intakes": {"egg": 2}})
    mock_response.model_dump.assert_called_once_with(by_alias=True)
