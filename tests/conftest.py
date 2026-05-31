from collections.abc import Callable, Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash

from diet.app import create_app
from diet.auth.models import User
from diet.body_composition.models import BodyComposition
from diet.extensions import sql_alchemy


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    app = create_app("testing")
    app_context = app.app_context()
    app_context.push()
    sql_alchemy.create_all()
    yield app
    sql_alchemy.session.remove()
    sql_alchemy.drop_all()
    app_context.pop()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_db(app: Flask) -> Generator[None, None, None]:
    yield
    sql_alchemy.session.rollback()
    sql_alchemy.session.query(BodyComposition).delete()
    sql_alchemy.session.query(User).delete()
    sql_alchemy.session.commit()


@pytest.fixture
def create_user() -> Callable[..., User]:
    def _create_user(
        username: str = "user1",
        email: str = "user1@example.com",
        password: str = "Password123!",
    ) -> User:
        user = User(username=username, email=email)
        user.password_hash = generate_password_hash(password)
        sql_alchemy.session.add(user)
        sql_alchemy.session.commit()
        return user

    return _create_user
