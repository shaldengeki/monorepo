from ..fitbit_client import FitbitClient
import logging


def test_signing_key():
    c = FitbitClient(
        logger=logging.Logger("test-fitbit-client"),
        client_id="test-client-id",
        client_secret="test-client-secret",
    )

    assert "test-client-secret&" == c.signing_key


def test_verify_signature_correct():
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


def test_verify_signature_invalid_header():
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


def test_verify_signature_invalid_body():
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


def test_authorization_token():
    c = FitbitClient(
        logger=logging.Logger("test-fitbit-client"),
        client_id="ABC123",
        client_secret="DEF456",
    )

    assert "QUJDMTIzOkRFRjQ1Ng==" == c.authorization_token


def test_code_challenge_from_verifier():
    assert (
        "-4cf-Mzo_qg9-uq0F4QwWhRh4AjcAqNx7SbYVsdmyQM"
        == FitbitClient.code_challenge_from_verifier(
            "01234567890123456789012345678901234567890123456789"
        )
    )


def test_authorization_url():
    c = FitbitClient(
        logger=logging.Logger("test-fitbit-client"),
        client_id="ABC123",
        client_secret="DEF456",
    )

    assert (
        "https://www.fitbit.com/oauth2/authorize?client_id=ABC123&response_type=code&code_challenge=-4cf-Mzo_qg9-uq0F4QwWhRh4AjcAqNx7SbYVsdmyQM&code_challenge_method=S256&scope=activity+heartrate+profile+social"
        == c.authorization_url("01234567890123456789012345678901234567890123456789")
    )
