from collections.abc import Callable

from flask.testing import FlaskClient
from pytest_mock import MockerFixture
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from diet.auth.constants import USERNAME_MAX_LENGTH
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


def test_signin_normalizes_email_before_authentication(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    create_user(email="signin@example.com", password="Password123!")

    response = client.post(
        "/auth/signin",
        data={
            "email": "  SIGNIN@example.com  ",
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
    assert (
        "サインインに失敗しました。メールアドレスまたはパスワードが正しくありません。".encode()
        in response.data
    )


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
    assert (
        "このメールアドレスはすでに登録されています。".encode()
        in response.data
    )


def test_signup_with_integrity_error_shows_existing_email_error(
    client: FlaskClient, mocker: MockerFixture
) -> None:
    mocker.patch(
        "diet.auth.service.create",
        side_effect=IntegrityError(None, None, Exception("unique constraint")),
    )

    response = client.post(
        "/auth/signup",
        data={
            "username": "new-user",
            "email": "race@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "sign_up": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert (
        "このメールアドレスはすでに登録されています。".encode()
        in response.data
    )


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
    assert "パスワードと一致している必要があります。".encode() in response.data


def test_signup_with_too_long_username_shows_validation_error(
    client: FlaskClient,
) -> None:
    response = client.post(
        "/auth/signup",
        data={
            "username": "a" * 81,
            "email": "too-long-username@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "sign_up": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert (
        f"1文字以上{USERNAME_MAX_LENGTH}文字以下で入力してください。".encode()  # noqa: E501
        in response.data
    )


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


def test_change_password_with_valid_credentials_redirects_account_menu(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    create_user(email="change-password@example.com", password="Password123!")
    client.post(
        "/auth/signin",
        data={
            "email": "change-password@example.com",
            "password": "Password123!",
            "sign_in": "1",
        },
    )

    response = client.post(
        "/auth/change_password",
        data={
            "current_password": "Password123!",
            "new_password": "NewPassword123!",
            "confirm_new_password": "NewPassword123!",
            "change_password": "1",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/account_menu")


def test_account_information_with_valid_username_redirects_self(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    create_user(email="account-info@example.com", password="Password123!")
    client.post(
        "/auth/signin",
        data={
            "email": "account-info@example.com",
            "password": "Password123!",
            "sign_in": "1",
        },
    )

    response = client.post(
        "/auth/account_information",
        data={"username": "updated-user", "update": "1"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/account_information")


def test_change_password_with_invalid_current_password_shows_error(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    create_user(email="wrong-current@example.com", password="Password123!")
    client.post(
        "/auth/signin",
        data={
            "email": "wrong-current@example.com",
            "password": "Password123!",
            "sign_in": "1",
        },
    )

    response = client.post(
        "/auth/change_password",
        data={
            "current_password": "wrong-password",
            "new_password": "NewPassword123!",
            "confirm_new_password": "NewPassword123!",
            "change_password": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "現在のパスワードが正しくありません。".encode() in response.data


def test_account_information_with_empty_username_shows_validation_error(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    create_user(email="empty-username@example.com", password="Password123!")
    client.post(
        "/auth/signin",
        data={
            "email": "empty-username@example.com",
            "password": "Password123!",
            "sign_in": "1",
        },
    )

    response = client.post(
        "/auth/account_information",
        data={"username": "", "update": "1"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "この項目は必須です。".encode() in response.data


def test_account_information_with_too_long_username_shows_validation_error(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    create_user(email="long-username@example.com", password="Password123!")
    client.post(
        "/auth/signin",
        data={
            "email": "long-username@example.com",
            "password": "Password123!",
            "sign_in": "1",
        },
    )

    response = client.post(
        "/auth/account_information",
        data={"username": "a" * 81, "update": "1"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert (
        f"1文字以上{USERNAME_MAX_LENGTH}文字以下で入力してください。".encode()  # noqa: E501
        in response.data
    )


def test_account_information_with_database_error_shows_error(
    client: FlaskClient,
    create_user: Callable[..., User],
    mocker: MockerFixture,
) -> None:
    create_user(email="username-db-error@example.com", password="Password123!")
    client.post(
        "/auth/signin",
        data={
            "email": "username-db-error@example.com",
            "password": "Password123!",
            "sign_in": "1",
        },
    )

    mocker.patch(
        "diet.auth.views.update_username",
        side_effect=SQLAlchemyError("db error"),
    )

    response = client.post(
        "/auth/account_information",
        data={"username": "updated-user", "update": "1"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert (
        "ユーザー名の変更に失敗しました。時間をおいて再度お試しください。".encode()
        in response.data
    )
