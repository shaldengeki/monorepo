import datetime
import requests

from base64 import b64encode
from datetime import timezone
from flask import abort, redirect, request, session
from graphql_server.flask import GraphQLView
from sqlalchemy.dialects.postgresql import insert
from typing import Optional
from urllib.parse import urlencode

from ..config import app, db, verify_fitbit_signature, verify_fitbit_verification
from .. import models
from . import gql

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql", schema=gql.Schema(models, app), graphiql=True
    ),
)


@app.route("/fitbit-notifications", methods=["GET"])
def fitbit_verification():
    if not request.args.get("verify", False):
        abort(404)

    if verify_fitbit_verification(request.args["verify"]):
        return "yay", 204
    else:
        abort(404)


@app.route("/fitbit-notifications", methods=["POST"])
def fitbit_notifications():
    if not verify_fitbit_signature(
        request.headers.get("X-Fitbit-Signature", ""), request.get_data()
    ):
        abort(400)

    for notification_data in request.json:
        subscription_notification = models.SubscriptionNotification(
            collection_type=notification_data["collectionType"],
            date=datetime.datetime.strptime(
                notification_data["date"], "%Y-%m-%d"
            ).astimezone(timezone.utc),
            fitbit_user_id=notification_data["ownerId"],
        )
        db.session.add(subscription_notification)
    db.session.commit()
    return "", 204


def get_token_data(
    client_id: str, client_secret: str, authorization_code: str, code_verifier: str
) -> Optional[dict]:
    encoded_client_and_secret = b64encode(
        f"{client_id}:{client_secret}".encode("utf-8")
    ).decode("utf-8")

    url_parameters = urlencode(
        {
            "client_id": client_id,
            "code": authorization_code,
            "code_verifier": code_verifier,
            "grant_type": "authorization_code",
        }
    )

    auth_request = requests.post(
        url="https://api.fitbit.com/oauth2/token?" + url_parameters,
        headers={
            "Authorization": f"Basic {encoded_client_and_secret}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data=url_parameters,
    )

    if auth_request.status_code != 200:
        return None

    return auth_request.json()


def fetch_display_name(user_id: str, access_token: str) -> str:
    profile_request = requests.get(
        f"https://api.fitbit.com/1/user/{user_id}/profile.json",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
    return profile_request.json()["user"]["displayName"]


def create_subscription(
    user_id: str, access_token: str, fitbit_subscription_id: int
) -> bool:
    sub_request = requests.post(
        f"https://api.fitbit.com/1/user/{user_id}/activities/apiSubscriptions/{fitbit_subscription_id}.json",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
        json={},
    )
    return sub_request.status_code in (200, 201)


@app.route("/fitbit-authorize", methods=["GET"])
def fitbit_authorize():
    if "code" not in request.args:
        abort(400)

    if "fitbit_code_verifier" not in session:
        abort(400)

    # Attempt to exchange the auth code for the access & refresh tokens.
    token_data = get_token_data(
        app.config["FITBIT_CLIENT_ID"],
        app.config["FITBIT_CLIENT_SECRET"],
        request.args["code"],
        session["fitbit_code_verifier"],
    )
    if token_data is None:
        abort(400)

    display_name = fetch_display_name(token_data["user_id"], token_data["access_token"])

    # Create or update a user object with the new tokens.
    insert_user = (
        insert(models.User.__table__)
        .values(
            fitbit_user_id=token_data["user_id"],
            display_name=display_name,
            fitbit_access_token=token_data["access_token"],
            fitbit_refresh_token=token_data["refresh_token"],
        )
        .on_conflict_do_update(
            constraint="users_pkey",
            set_={
                "display_name": display_name,
                "fitbit_access_token": token_data["access_token"],
                "fitbit_refresh_token": token_data["refresh_token"],
            },
        )
    )
    db.session.execute(insert_user)
    db.session.commit()

    user = models.User.query.filter(
        models.User.fitbit_user_id == token_data["user_id"]
    ).first()

    create_subscription(
        token_data["user_id"], token_data["access_token"], user.fitbit_subscription_id
    )

    session["fitbit_user_id"] = token_data["user_id"]
    return redirect(app.config["FRONTEND_URL"])
