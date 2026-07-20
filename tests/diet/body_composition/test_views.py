import datetime
from collections.abc import Callable

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from diet.auth.models import User
from diet.body_composition.models import BodyComposition
from diet.extensions import sql_alchemy


def _signin(client: FlaskClient, email: str, password: str) -> None:
    client.post(
        "/auth/signin",
        data={"email": email, "password": password, "sign_in": "1"},
    )


def test_record_body_composition_requires_login(client: FlaskClient) -> None:
    response = client.get(
        "/body_composition/record_body_composition", follow_redirects=False
    )

    assert response.status_code == 302
    assert "/auth/signin" in response.headers["Location"]


def test_record_body_composition_get_sets_latest_values(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    user = create_user(email="bc@example.com", password="Password123!")
    sql_alchemy.session.add(
        BodyComposition(
            date=datetime.date(2026, 5, 20),
            weight=70.5,
            body_fat=20.1,
            user_id=user.id,
        )
    )
    sql_alchemy.session.commit()
    _signin(client, "bc@example.com", "Password123!")

    response = client.get("/body_composition/record_body_composition")

    assert response.status_code == 200
    assert b'value="70.5"' in response.data
    assert b'value="20.1"' in response.data


@pytest.mark.parametrize(
    ("language", "expected_message"),
    [
        ("ja", "体組成データを保存しました。"),
        ("en", "Body composition data saved successfully."),
    ],
)
def test_record_body_composition_post_valid_data_saves_and_redirects(
    client: FlaskClient,
    create_user: Callable[..., User],
    language: str,
    expected_message: str,
) -> None:
    user = create_user(email="bc@example.com", password="Password123!")
    _signin(client, "bc@example.com", "Password123!")

    response = client.post(
        f"/body_composition/record_body_composition?lang={language}",
        data={
            "date": "2026-05-24",
            "weight": "72.3",
            "body_fat": "19.5",
            "submit": "1",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    redirected_response = client.get(response.headers["Location"])
    assert expected_message.encode() in redirected_response.data

    record = BodyComposition.query.filter_by(
        user_id=user.id, date=datetime.date(2026, 5, 24)
    ).first()
    assert record is not None
    assert record.weight == 72.3
    assert record.body_fat == 19.5


@pytest.mark.parametrize(
    ("language", "expected_message"),
    [
        ("ja", "入力内容に問題があります。内容を確認してください。"),
        ("en", "There is a problem with the input. Please review it."),
    ],
)
def test_record_body_composition_does_not_expose_internal_validation_error(
    client: FlaskClient,
    create_user: Callable[..., User],
    mocker: MockerFixture,
    language: str,
    expected_message: str,
) -> None:
    create_user(email="validation@example.com", password="Password123!")
    _signin(client, "validation@example.com", "Password123!")
    mocker.patch(
        "diet.body_composition.views.upsert_body_composition",
        side_effect=ValueError("internal validation details"),
    )

    response = client.post(
        f"/body_composition/record_body_composition?lang={language}",
        data={
            "date": "2026-05-24",
            "weight": "72.3",
            "body_fat": "19.5",
            "submit": "1",
        },
    )

    assert response.status_code == 200
    assert expected_message.encode() in response.data
    assert b"internal validation details" not in response.data


def test_record_body_composition_post_invalid_data_shows_error(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    create_user(email="bc@example.com", password="Password123!")
    _signin(client, "bc@example.com", "Password123!")

    response = client.post(
        "/body_composition/record_body_composition",
        data={
            "date": "2026-05-24",
            "weight": "0",
            "body_fat": "120",
            "submit": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "0.1以上300.0以下で入力してください。".encode() in response.data
    assert "0.1以上99.9以下で入力してください。".encode() in response.data


def test_record_body_composition_updates_existing_value(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    user = create_user(email="bc@example.com", password="Password123!")
    sql_alchemy.session.add(
        BodyComposition(
            date=datetime.date(2026, 5, 24),
            weight=70.0,
            body_fat=20.0,
            user_id=user.id,
        )
    )
    sql_alchemy.session.commit()
    _signin(client, "bc@example.com", "Password123!")

    client.post(
        "/body_composition/record_body_composition",
        data={
            "date": "2026-05-24",
            "weight": "71.2",
            "body_fat": "19.8",
            "submit": "1",
        },
    )

    record = BodyComposition.query.filter_by(
        user_id=user.id, date=datetime.date(2026, 5, 24)
    ).first()
    assert record is not None
    assert record.weight == 71.2
    assert record.body_fat == 19.8


def test_get_body_composition_data_for_anonymous_returns_sample(
    client: FlaskClient,
) -> None:
    response = client.get("/body_composition/get_body_composition_data")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None
    assert len(payload["bodyCompositions"]) > 0
    assert "date" in payload["bodyCompositions"][0]
    assert "weight" in payload["bodyCompositions"][0]
    assert "bodyFat" in payload["bodyCompositions"][0]
    assert "monthlyStatistics" in payload


def test_get_body_composition_data_for_auth_user_without_records_returns_empty(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    create_user(email="empty-bc@example.com", password="Password123!")
    _signin(client, "empty-bc@example.com", "Password123!")

    response = client.get("/body_composition/get_body_composition_data")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload == {"bodyCompositions": [], "monthlyStatistics": []}


def test_get_body_composition_data_for_authenticated_user_returns_records(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    user = create_user(email="bc@example.com", password="Password123!")
    sql_alchemy.session.add(
        BodyComposition(
            date=datetime.date(2026, 5, 24),
            weight=66.6,
            body_fat=18.2,
            user_id=user.id,
        )
    )
    sql_alchemy.session.commit()
    _signin(client, "bc@example.com", "Password123!")

    response = client.get("/body_composition/get_body_composition_data")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None
    assert payload["bodyCompositions"][0]["date"] == "2026-05-24"
    assert payload["bodyCompositions"][0]["weight"] == 66.6
    assert payload["bodyCompositions"][0]["bodyFat"] == 18.2
