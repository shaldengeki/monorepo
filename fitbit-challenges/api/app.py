import datetime
from datetime import timezone
from flask import abort, request
from graphql_server.flask import GraphQLView

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
