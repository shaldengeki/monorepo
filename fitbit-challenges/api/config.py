import base64
import hmac
import hashlib
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)

frontend_url_parts = [
    os.getenv("FRONTEND_PROTOCOL", "http"),
    "://",
    os.getenv("FRONTEND_HOST", "localhost"),
]
if os.getenv("FRONTEND_PORT", None):
    frontend_url_parts.append(":" + os.getenv("FRONTEND_PORT", "5001"))

frontend_url = "".join(frontend_url_parts)

app.config.update(
    FITBIT_CLIENT_ID=os.getenv("FITBIT_CLIENT_ID", "testing"),
    FITBIT_SIGNING_KEY=os.getenv("FITBIT_CLIENT_SECRET", "testing") + "&",
    FRONTEND_URL=frontend_url,
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "testing"),
    SQLALCHEMY_DATABASE_URI="postgresql://{user}:{password}@{host}/{db}".format(
        user=os.getenv("DB_USERNAME", "admin"),
        password=os.getenv("DB_PASSWORD", "development"),
        host=os.getenv("DB_HOST", "pg"),
        db=os.getenv("DATABASE_NAME", "api_development"),
    ),
)


def verify_fitbit_signature(header_signature: str, json_body: bytes) -> bool:
    digest = hmac.digest(
        app.config["FITBIT_SIGNING_KEY"].encode("utf-8"), json_body, hashlib.sha1
    )
    b64_encoded = base64.b64encode(digest)
    return header_signature.encode("utf-8") == b64_encoded


def verify_fitbit_verification(request_code: str) -> bool:
    return request_code == os.getenv("FITBIT_VERIFICATION_CODE", "testing")


CORS(
    app,
    resources={
        "/graphql": {
            "origins": [frontend_url],
        }
    },
)

db = SQLAlchemy(app)

migrate = Migrate(app, db)
