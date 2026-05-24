import re

from flask import Flask
from flask.testing import FlaskClient

_OPTIMIZE_REQUEST_JSON = {
    "foodInformation": [
        {
            "name": "boiled_egg",
            "energy": 134,
            "protein": 12.5,
            "fat": 10.4,
            "carbohydrates": 0.3,
            "gramsPerUnit": 50,
            "minimumIntake": 1,
            "maximumIntake": 3,
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
            "value": 200,
        },
        {
            "minMax": "min",
            "nutrient": "fat",
            "unit": "ratio",
            "value": 20,
        },
    ],
}


def test_index_page(client: FlaskClient) -> None:
    response = client.get("/nutrition_optimizer/")

    assert response.status_code == 200
    assert b'<meta name="csrf-token"' in response.data


def test_optimize(client: FlaskClient) -> None:
    response = client.post(
        "/nutrition_optimizer/optimize",
        json=_OPTIMIZE_REQUEST_JSON,
    )

    assert response.status_code == 200
    assert response.json is not None
    assert response.json["status"] == "Optimal"
    assert response.json["foodIntakes"]["boiled_egg"] == 2


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


def test_optimize_with_invalid_request_returns_bad_request(
    client: FlaskClient,
) -> None:
    response = client.post(
        "/nutrition_optimizer/optimize",
        json={"objective": {"sense": "maximize"}},
    )

    assert response.status_code == 400
    assert response.json is not None
    assert response.json["status"] == "Error"
