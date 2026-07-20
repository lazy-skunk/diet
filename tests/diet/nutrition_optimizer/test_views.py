import json
import re

from flask import Flask
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

_OPTIMIZE_REQUEST_JSON = {
    "foodSelections": [
        {
            "foodName": "アマランサス　玄穀",
            "energy": 343,
            "protein": 12.7,
            "fat": 6.0,
            "carbohydrates": 64.9,
            "minimumIntakeGrams": 100,
            "maximumIntakeGrams": 300,
        }
    ],
    "objective": {
        "sense": "maximize",
        "nutrient": "energy",
    },
    "constraints": [
        {
            "minMax": "max",
            "nutrient": "energy",
            "unit": "energy",
            "value": 1000,
        },
        {
            "minMax": "min",
            "nutrient": "fat",
            "unit": "pfc_ratio",
            "value": 10,
        },
    ],
}


def _nutrient_definitions(response_data: bytes) -> dict[str, dict[str, str]]:
    match = re.search(
        rb'<script id="nutrient-definition-data"[^>]*>(.*?)</script>',
        response_data,
    )
    assert match is not None
    return {
        definition["identifier"]: definition
        for definition in json.loads(match.group(1))
    }


def test_index_page(client: FlaskClient) -> None:
    response = client.get("/nutrition_optimizer/")

    assert response.status_code == 200
    assert b'<meta name="csrf-token"' in response.data
    assert b'id="nutrient-display-filters"' not in response.data
    assert b'id="nutrient-filter-search"' not in response.data
    assert b'id="food-picker-modal"' in response.data
    assert b'id="add-food"' not in response.data
    assert b"data-add-food-row" in response.data
    assert b"data-remove-food-row" in response.data
    assert (
        b"data-remove-food-row\n                                disabled"
        in response.data
    )
    assert b'id="add-constraint"' not in response.data
    assert b"data-add-constraint-row" in response.data
    assert b"data-remove-constraint-row" in response.data
    assert (
        b"data-remove-constraint-row\n                            disabled"
        in response.data
    )
    assert b'id="food-picker-search"' in response.data
    assert b'id="food-picker-result-count"' in response.data
    assert b'id="food-picker-previous"' in response.data
    assert b'id="food-picker-next"' in response.data
    assert b'id="food-picker-page-status"' in response.data
    assert "該当する食品がありません。".encode() in response.data
    assert b'id="food-catalog-data"' not in response.data
    assert (
        b'data-food-catalog-url="/nutrition_optimizer/static/data/'
        b'food_master.min.json"' in response.data
    )
    assert b'id="nutrient-definition-data"' in response.data
    assert b'"identifier": "ENERC_KCAL"' in response.data
    assert b'"identifier": "PROT-"' in response.data
    assert b'"identifier": "FAT-"' in response.data
    assert b'"identifier": "CHOCDF-"' in response.data
    assert b'"identifier": "FIB-"' not in response.data
    nutrient_definitions = _nutrient_definitions(response.data)
    assert nutrient_definitions["ENERC_KCAL"]["name"] == "エネルギー"
    assert nutrient_definitions["ENERC_KCAL"]["key"] == "energy"
    assert nutrient_definitions["ENERC_KCAL"]["displayUnit"] == "kcal/100g"
    assert nutrient_definitions["PROT-"]["name"] == "たんぱく質"
    assert nutrient_definitions["PROT-"]["displayUnit"] == "g/100g"
    assert nutrient_definitions["FAT-"]["name"] == "脂質"
    assert nutrient_definitions["CHOCDF-"]["name"] == "炭水化物"
    assert nutrient_definitions["CHOCDF-"]["key"] == "carbohydrates"
    assert "食品名を入力、または食品一覧から選択".encode() in response.data
    assert "最小摂取量 (g)".encode() in response.data
    assert "最大摂取量 (g)".encode() in response.data
    assert response.data.count(b'step="1"') == 4
    assert "1単位あたりのグラム数".encode() not in response.data


def test_food_master_is_served_as_static_json(client: FlaskClient) -> None:
    response = client.get(
        "/nutrition_optimizer/static/data/food_master.min.json"
    )

    assert response.status_code == 200
    assert response.is_json
    food_master = response.get_json()
    nutrient_identifiers = food_master["nutrientIdentifiers"]
    foods = food_master["foods"]
    first_food_values = dict(
        zip(nutrient_identifiers, foods[0]["values"], strict=True)
    )

    assert len(nutrient_identifiers) == 33
    assert len(foods) == 2538
    assert foods[0]["name"] == "アマランサス　玄穀"
    assert first_food_values["ENERC_KCAL"] == "343"
    assert first_food_values["PROT-"] == "12.7"
    assert first_food_values["FAT-"] == "6.0"
    assert first_food_values["CHOCDF-"] == "64.9"
    assert first_food_values["VITK"] == "(0)"


def test_index_page_translates_nutrient_names(client: FlaskClient) -> None:
    response = client.get("/nutrition_optimizer/?lang=en")

    assert response.status_code == 200
    nutrient_definitions = _nutrient_definitions(response.data)
    assert nutrient_definitions["ENERC_KCAL"]["name"] == "Energy"
    assert nutrient_definitions["PROT-"]["name"] == "Protein"
    assert nutrient_definitions["FAT-"]["name"] == "Fat"
    assert nutrient_definitions["CHOCDF-"]["name"] == "Carbohydrates"


def test_optimize(client: FlaskClient) -> None:
    response = client.post(
        "/nutrition_optimizer/optimize",
        json=_OPTIMIZE_REQUEST_JSON,
    )

    assert response.status_code == 200
    assert response.json is not None
    assert response.json["status"] == "Optimal"
    assert response.json["foodIntakeGrams"]["アマランサス　玄穀"] == 291
    assert "pfcCompositionRatio" in response.json


def test_optimize_with_manual_food_input(client: FlaskClient) -> None:
    response = client.post(
        "/nutrition_optimizer/optimize",
        json={
            "foodSelections": [
                {
                    "foodName": "manual tofu",
                    "energy": 80,
                    "protein": 7.0,
                    "fat": 4.0,
                    "carbohydrates": 2.0,
                    "minimumIntakeGrams": 100,
                    "maximumIntakeGrams": 200,
                }
            ],
            "objective": {
                "sense": "maximize",
                "nutrient": "energy",
            },
            "constraints": [
                {
                    "minMax": "max",
                    "nutrient": "energy",
                    "unit": "energy",
                    "value": 1000,
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json is not None
    assert response.json["status"] == "Optimal"
    assert response.json["foodIntakeGrams"] == {"manual tofu": 200}


def test_optimize_with_csrf_enabled(app: Flask, client: FlaskClient) -> None:
    app.config["WTF_CSRF_ENABLED"] = True

    index_response = client.get("/nutrition_optimizer/")
    html = index_response.data.decode()
    match = re.search(r'<meta name="csrf-token" content="([^"]+)"', html)

    assert match is not None

    response = client.post(
        "/nutrition_optimizer/optimize",
        headers={"X-CSRFToken": match.group(1)},
        json=_OPTIMIZE_REQUEST_JSON,
    )

    assert response.status_code == 200
    assert response.json is not None
    assert response.json["status"] == "Optimal"


def test_optimize_with_invalid_csrf_returns_json(
    app: Flask, client: FlaskClient
) -> None:
    app.config["WTF_CSRF_ENABLED"] = True

    response = client.post(
        "/nutrition_optimizer/optimize",
        headers={"X-CSRFToken": "invalid"},
        json=_OPTIMIZE_REQUEST_JSON,
    )

    assert response.status_code == 400
    assert response.is_json
    assert response.json == {
        "status": "Error",
        "errorCode": "request_verification_failed",
    }


def test_optimize_with_invalid_request_returns_bad_request(
    client: FlaskClient,
) -> None:
    response = client.post(
        "/nutrition_optimizer/optimize",
        json={"objective": {"sense": "maximize"}},
    )

    assert response.status_code == 400
    assert response.json == {
        "status": "Error",
        "errorCode": "invalid_input",
    }


def test_optimize_with_unexpected_error_hides_internal_details(
    client: FlaskClient, mocker: MockerFixture
) -> None:
    mocker.patch(
        "diet.nutrition_optimizer.views.optimize_nutrition",
        side_effect=RuntimeError("solver exploded"),
    )

    response = client.post(
        "/nutrition_optimizer/optimize",
        json=_OPTIMIZE_REQUEST_JSON,
    )

    assert response.status_code == 500
    assert response.json == {
        "status": "Error",
        "errorCode": "unexpected_response",
    }


def test_optimize_with_internal_value_error_returns_server_error(
    client: FlaskClient, mocker: MockerFixture
) -> None:
    mocker.patch(
        "diet.nutrition_optimizer.views.optimize_nutrition",
        side_effect=ValueError("internal implementation detail"),
    )

    response = client.post(
        "/nutrition_optimizer/optimize",
        json=_OPTIMIZE_REQUEST_JSON,
    )

    assert response.status_code == 500
    assert response.json == {
        "status": "Error",
        "errorCode": "unexpected_response",
    }
