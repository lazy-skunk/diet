from flask.testing import FlaskClient


def test_index_page(client: FlaskClient) -> None:
    response = client.get("/nutrition_optimizer/")

    assert response.status_code == 200


def test_optimize(client: FlaskClient) -> None:
    response = client.post(
        "/nutrition_optimizer/optimize",
        json={
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
        },
    )

    assert response.status_code == 200
    assert response.json is not None
    assert response.json["status"] == "Optimal"
    assert response.json["foodIntakes"]["boiled_egg"] == 2
