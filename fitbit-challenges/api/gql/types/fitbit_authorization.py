from base64 import b64encode
import dataclasses
from flask import session
from hashlib import sha256
import secrets
from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLNonNull,
    GraphQLString,
)
from urllib.parse import urlencode
from ...config import app


def fitbit_authorization_fields() -> dict[str, GraphQLField]:
    return {
        "url": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The URL that the user should be redirected to in order to complete Fitbit authorization.",
        ),
    }


fitbit_authorization_type = GraphQLObjectType(
    "FitbitAuthorization",
    description="The first step of a Fitbit authorization.",
    fields=fitbit_authorization_fields,
)


@dataclasses.dataclass
class FitbitAuthorization:
    url: str


def authorize_with_fitbit(fitbit_client_id: str):
    if "fitbit_code_verifier" not in session:
        code_verifier = secrets.token_hex()
        session["fitbit_code_verifier"] = code_verifier
    code_challenge = (
        b64encode(sha256(code_verifier.encode("utf-8")).digest())
        .decode("utf-8")
        .rstrip("=")
        .replace("+", "-")
        .replace("/", "_")
    )
    collections = ["activity", "heartrate", "profile", "social"]

    url_parameters = {
        "client_id": fitbit_client_id,
        "response_type": "code",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "scope": " ".join(collections),
    }
    url = "https:///www.fitbit.com/oauth2/authorize?" + urlencode(url_parameters)
    return FitbitAuthorization(url=url)


def authorize_with_fitbit_field(app) -> GraphQLField:
    return GraphQLField(
        fitbit_authorization_type,
        resolve=lambda root, info, **args: authorize_with_fitbit(
            app.config["FITBIT_CLIENT_ID"]
        ),
    )
