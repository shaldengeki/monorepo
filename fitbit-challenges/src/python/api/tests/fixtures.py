import flask
import pytest

from flask.testing import FlaskClient, FlaskCliRunner
from typing import Iterator

from ..app import app as base_app


@pytest.fixture
def app() -> Iterator[flask.Flask]:
    base_app.config.update(
        {
            "TESTING": True,
        }
    )
    yield base_app


@pytest.fixture
def client(app: flask.Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: flask.Flask) -> FlaskCliRunner:
    return app.test_cli_runner()
