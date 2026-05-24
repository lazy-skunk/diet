from collections.abc import Callable

from flask.testing import FlaskClient

from diet.auth.models import User


def test_signin_page(client: FlaskClient) -> None:
    response = client.get("/auth/signin")
    assert response.status_code == 200


def test_signin_with_valid_credentials_redirects_home(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    create_user(email="signin@example.com", password="Password123!")

    response = client.post(
        "/auth/signin",
        data={
            "email": "signin@example.com",
            "password": "Password123!",
            "sign_in": "1",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_signin_with_invalid_credentials_shows_error(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    create_user(email="signin@example.com", password="Password123!")

    response = client.post(
        "/auth/signin",
        data={
            "email": "signin@example.com",
            "password": "wrong-password",
            "sign_in": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Sign-in failed. Invalid email or password." in response.data


def test_signup_page(client: FlaskClient) -> None:
    response = client.get("/auth/signup")
    assert response.status_code == 200


def test_signup_with_existing_email_shows_error(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    create_user(email="dup@example.com")

    response = client.post(
        "/auth/signup",
        data={
            "username": "new-user",
            "email": "dup@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "sign_up": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Sign-up failed. Please try again later." in response.data


def test_signup_with_password_mismatch_shows_validation_error(
    client: FlaskClient,
) -> None:
    response = client.post(
        "/auth/signup",
        data={
            "username": "new-user",
            "email": "new-user@example.com",
            "password": "Password123!",
            "confirm_password": "Password999!",
            "sign_up": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Field must be equal to password." in response.data


def test_signout_redirects_signin_when_not_authenticated(
    client: FlaskClient,
) -> None:
    response = client.get("/auth/signout", follow_redirects=False)

    assert response.status_code == 302
    assert "/auth/signin" in response.headers["Location"]


def test_signout_redirects_home_when_authenticated(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    create_user(email="signout@example.com", password="Password123!")
    client.post(
        "/auth/signin",
        data={
            "email": "signout@example.com",
            "password": "Password123!",
            "sign_in": "1",
        },
    )

    response = client.get("/auth/signout", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
