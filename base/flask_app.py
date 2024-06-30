import datetime
import os
from typing import Optional

from flask import Flask, session
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


def FlaskApp(name) -> tuple[Flask, CORS, SQLAlchemy, Migrate]:
    app = Flask(name)

    frontend_url_parts = [
        os.getenv("FRONTEND_PROTOCOL", "http"),
        "://",
        os.getenv("FRONTEND_HOST", "localhost"),
    ]
    if os.getenv("FRONTEND_PORT", None):
        frontend_url_parts.append(":" + os.getenv("FRONTEND_PORT", "5001"))

    frontend_url = "".join(frontend_url_parts)

    app.config.update(
        FRONTEND_URL=frontend_url,
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "testing"),
        SQLALCHEMY_DATABASE_URI="postgresql+pg8000://{user}:{password}@{host}/{db}".format(
            user=os.getenv("DB_USERNAME", "admin"),
            password=os.getenv("DB_PASSWORD", "development"),
            host=os.getenv("DB_HOST", "pg"),
            db=os.getenv("DATABASE_NAME", "api_development"),
        ),
        SESSION_REFRESH_EACH_REQUEST=True,
        PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=365),
    )

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    cors = CORS(
        app,
        resources={
            "/graphql": {
                "origins": [frontend_url],
            }
        },
        supports_credentials=True,
    )

    db = SQLAlchemy(
        app,
        session_options={
            "autoflush": False,
        },
    )

    migrate = Migrate(app, db)

    return (app, cors, db, migrate)
