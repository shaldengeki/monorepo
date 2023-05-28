import datetime
import requests

from base64 import b64encode
from datetime import timezone
from flask import abort, redirect, request, session
from graphql_server.flask import GraphQLView
from sqlalchemy.dialects.postgresql import insert
from urllib.parse import urlencode

from .config import app, db, verify_fitbit_signature, verify_fitbit_verification
from . import models
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


@app.route("/fitbit-authorize", methods=["GET"])
def fitbit_authorize():
    if "code" not in request.args:
        abort(400)
    authorization_code = request.args["code"]

    if "fitbit_code_verifier" not in session:
        abort(400)
    code_verifier = session["fitbit_code_verifier"]

    # Attempt to exchange the auth code for the access & refresh tokens.
    encoded_client_and_secret = b64encode(
        f"{app.config['FITBIT_CLIENT_ID']}:{app.config['FITBIT_CLIENT_SECRET']}".encode(
            "utf-8"
        )
    ).decode("utf-8")

    url_parameters = urlencode(
        {
            "client_id": app.config["FITBIT_CLIENT_ID"],
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
        abort(400)

    response = auth_request.json()

    # Create or update a user object with the new tokens.
    insert_user = (
        insert(models.User.__table__)
        .values(
            fitbit_user_id=response["user_id"],
            fitbit_access_token=response["access_token"],
            fitbit_refresh_token=response["refresh_token"],
        )
        .on_conflict_do_update(
            constraint="users_pkey",
            set_={
                "fitbit_access_token": response["access_token"],
                "fitbit_refresh_token": response["refresh_token"],
            },
        )
    )
    db.session.execute(insert_user)
    db.session.commit()

    session["fitbit_user_id"] = response["user_id"]
    return redirect(app.config["FRONTEND_URL"])
