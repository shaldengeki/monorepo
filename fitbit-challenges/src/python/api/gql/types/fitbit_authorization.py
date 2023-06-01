import dataclasses
from flask import session
import secrets
from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLNonNull,
    GraphQLString,
)

from ....fitbit_client import FitbitClient


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


def authorize_with_fitbit(fitbit_client: FitbitClient):
    if "fitbit_code_verifier" not in session:
        code_verifier = secrets.token_hex()
        session["fitbit_code_verifier"] = code_verifier
    else:
        code_verifier = session["fitbit_code_verifier"]

    return FitbitAuthorization(url=fitbit_client.authorization_url(code_verifier))


def authorize_with_fitbit_field(app) -> GraphQLField:
    return GraphQLField(
        fitbit_authorization_type,
        resolve=lambda root, info, **args: authorize_with_fitbit(
            app.config["FITBIT_CLIENT"]
        ),
    )
