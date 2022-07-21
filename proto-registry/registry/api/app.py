import json
from flask import abort
from sqlalchemy import asc

from .config import app
from . import models

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/subjects")
def subjects():
    return json.dumps([dict(x) for x in models.Subject.query.order_by(asc(models.Subject.id)).all()])

@app.route("/subjects/<subject_name>/versions")
def subject_versions(subject_name):
    subject = models.Subject.query.filter(models.Subject.name == subject_name).first()
    if subject is None:
        abort(404)

    return json.dumps([
        version.version_id
        for version in subject.versions
    ])

@app.route("/subjects/<subject_name>/versions/<int:version_id>")
def subject_version(subject_name, version_id):
    subject = models.Subject.query.filter(models.Subject.name == subject_name).first()
    if subject is None:
        abort(404)

    versions = [v for v in subject.versions if v.version_id == version_id]
    if not versions:
        abort(404)
    return next(versions).schema

if __name__ == "__main__":
    app.run()
