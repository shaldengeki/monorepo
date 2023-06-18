import datetime

from datetime import timezone
from flask import abort, redirect, request, session
from graphql_server.flask import GraphQLView  # type: ignore
from typing import Optional

from ..config import app, db, verify_fitbit_verification
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
    if not app.config["FITBIT_CLIENT"].verify_signature(
        request.headers.get("X-Fitbit-Signature", ""), request.get_data()
    ):
        abort(400)

    if not isinstance(request.json, list):
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

    if "fitbit_code_verifier" not in session:
        abort(400)

    # Attempt to exchange the auth code for the access & refresh tokens.
    token_data = app.config["FITBIT_CLIENT"].get_token_data(
        request.args["code"], session["fitbit_code_verifier"]
    )
    if token_data is None:
        abort(400)

    # Create or update a user object with the new tokens.
    db.session.execute(
        models.User.create_with_user_id_and_tokens(
            token_data["user_id"],
            token_data["access_token"],
            token_data["refresh_token"],
        )
    )
    db.session.commit()

    user: models.User = models.User.query.filter(
        models.User.fitbit_user_id == token_data["user_id"]
    ).first()
    subscription: Optional[models.FitbitSubscription] = user.create_subscription(
        app.config["FITBIT_CLIENT"]
    )
    db.session.add(user)
    if subscription is not None:
        db.session.add(subscription)
    db.session.commit()

    session["fitbit_user_id"] = token_data["user_id"]
    return redirect(app.config["FRONTEND_URL"])
