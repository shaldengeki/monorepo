import os

from base.flask_app import FlaskApp

app, cors, db, migrate = FlaskApp(__name__)
