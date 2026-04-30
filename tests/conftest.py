from collections.abc import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from diet.app import create_app


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    app = create_app("testing")
    app_context = app.app_context()
    app_context.push()
    yield app
    app_context.pop()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()
