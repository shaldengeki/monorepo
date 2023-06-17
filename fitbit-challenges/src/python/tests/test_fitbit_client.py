import datetime
from ..fitbit_client import FitbitClient
import logging
import pytest
import requests
from typing import Optional


@pytest.fixture
def default_client():
    return FitbitClient(
        logger=logging.Logger("test-fitbit-client"),
        client_id="test-client-id",
        client_secret="test-client-secret",
    )


class MockPost:
    def __init__(
        self,
        response: dict[str, str],
        status_code: int,
        url: str = "test-url",
        headers: Optional[dict[str, str]] = None,
    ):
        self.response = response
        self.status_code = status_code
        self.url = url
        if headers is None:
            headers = {}
        self.headers = headers
        self.text = str(self.response)

    def json(self):
        return self.response


def test_signing_key(default_client) -> None:
    assert "test-client-secret&" == default_client.signing_key


def test_verify_signature_correct() -> None:
    c = FitbitClient(
        logger=logging.Logger("test-fitbit-client"),
        client_id="test-client-id",
        client_secret="123ab4567c890d123e4567f8abcdef9a",
    )

    json_body = """[
  {
    "collectionType": "foods",
    "date": "2020-06-01",
    "ownerId": "228S74",
    "ownerType": "user",
    "subscriptionId": "1234"
  }
]""".encode(
        "utf-8"
    )

    assert c.verify_signature("Oyv+HBziS4dH/fHJ735cToXX6vs=", json_body)


def test_verify_signature_invalid_header() -> None:
    c = FitbitClient(
        logger=logging.Logger("test-fitbit-client"),
        client_id="test-client-id",
        client_secret="123ab4567c890d123e4567f8abcdef9a",
    )

    json_body = """[
  {
    "collectionType": "foods",
    "date": "2020-06-01",
    "ownerId": "228S74",
    "ownerType": "user",
    "subscriptionId": "1234"
  }
]""".encode(
        "utf-8"
    )

    assert not c.verify_signature("WRONG-HEADER-SIGNATURE", json_body)


def test_verify_signature_invalid_body() -> None:
    c = FitbitClient(
        logger=logging.Logger("test-fitbit-client"),
        client_id="test-client-id",
        client_secret="123ab4567c890d123e4567f8abcdef9a",
    )

    json_body = """[
  {
    "collectionType": "INCORRECTVALUE",
    "date": "2020-06-01",
    "ownerId": "228S74",
    "ownerType": "user",
    "subscriptionId": "1234"
  }
]""".encode(
        "utf-8"
    )

    assert not c.verify_signature("Oyv+HBziS4dH/fHJ735cToXX6vs=", json_body)


def test_authorization_token() -> None:
    c = FitbitClient(
        logger=logging.Logger("test-fitbit-client"),
        client_id="ABC123",
        client_secret="DEF456",
    )

    assert "QUJDMTIzOkRFRjQ1Ng==" == c.authorization_token


def test_code_challenge_from_verifier() -> None:
    assert (
        "-4cf-Mzo_qg9-uq0F4QwWhRh4AjcAqNx7SbYVsdmyQM"
        == FitbitClient.code_challenge_from_verifier(
            "01234567890123456789012345678901234567890123456789"
        )
    )


def test_authorization_url() -> None:
    c = FitbitClient(
        logger=logging.Logger("test-fitbit-client"),
        client_id="ABC123",
        client_secret="DEF456",
    )

    assert (
        "https://www.fitbit.com/oauth2/authorize?client_id=ABC123&response_type=code&code_challenge=-4cf-Mzo_qg9-uq0F4QwWhRh4AjcAqNx7SbYVsdmyQM&code_challenge_method=S256&scope=activity+heartrate+profile+social"
        == c.authorization_url("01234567890123456789012345678901234567890123456789")
    )


def test_get_token_data_with_successful_request(
    default_client: FitbitClient, monkeypatch
) -> None:
    response = {"expected_field": "expected_value"}

    def mock_post(*args, **kwargs) -> MockPost:
        return MockPost(response, 200)

    monkeypatch.setattr(requests, "post", mock_post)
    assert response == default_client.get_token_data(
        "test-auth-code", "test-code-verifier"
    )


def test_get_token_data_with_failed_request(
    default_client: FitbitClient, monkeypatch
) -> None:
    response = None

    def mock_post(*args, **kwargs) -> MockPost:
        return MockPost(response, 400)

    monkeypatch.setattr(requests, "post", mock_post)
    assert response == default_client.get_token_data(
        "test-auth-code", "test-code-verifier"
    )


def test_get_user_daily_activity_summary_with_successful_request(
    default_client: FitbitClient, monkeypatch
) -> None:
    response = {"expected_field": "expected_value"}

    def mock_get(*args, **kwargs) -> MockPost:
        return MockPost(response, 200)

    monkeypatch.setattr(requests, "get", mock_get)
    assert response == default_client.get_user_daily_activity_summary(
        "test-user-id", "test-access-token", datetime.datetime.now()
    )


def test_get_user_daily_activity_summary_with_failed_request(
    default_client: FitbitClient, monkeypatch
) -> None:
    response = {"errors": ["some errors"]}

    def mock_get(*args, **kwargs) -> MockPost:
        return MockPost(response, 400)

    monkeypatch.setattr(requests, "get", mock_get)
    assert response == default_client.get_user_daily_activity_summary(
        "test-user-id", "test-access-token", datetime.datetime.now()
    )


def test_refresh_user_tokens_with_successful_request(
    default_client: FitbitClient, monkeypatch
) -> None:
    response = {"expected_field": "expected_value"}

    def mock_post(*args, **kwargs) -> MockPost:
        return MockPost(response, 200)

    monkeypatch.setattr(requests, "post", mock_post)
    assert response == default_client.refresh_user_tokens("test-refresh-token")


def test_refresh_user_tokens_with_failed_request(
    default_client: FitbitClient, monkeypatch
) -> None:
    response = None

    def mock_post(*args, **kwargs) -> MockPost:
        return MockPost(response, 400)

    monkeypatch.setattr(requests, "post", mock_post)
    with pytest.raises(ValueError):
        default_client.refresh_user_tokens("test-refresh-token")
