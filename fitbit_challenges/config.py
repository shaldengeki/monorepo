import os

from base.flask_app import FlaskApp
from fitbit_challenges.fitbit_client import FitbitClient

def create_schema(app):
    from fitbit_challenges import models
    from fitbit_challenges.api import gql
    return gql.Schema(models, app)


app, cors, db, migrate = FlaskApp(
    __name__,
    create_schema,
)

app.config.update(
    FITBIT_CLIENT=FitbitClient(
        logger=app.logger,
        client_id=os.getenv("FITBIT_CLIENT_ID", "testing"),
        client_secret=os.getenv("FITBIT_CLIENT_SECRET", "testing"),
    ),
)


def verify_fitbit_verification(request_code: str) -> bool:
    return request_code == os.getenv("FITBIT_VERIFICATION_CODE", "testing")
