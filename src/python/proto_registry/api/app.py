import json

from api import models
from api.config import app, db
from flask import abort, request
from sqlalchemy import asc


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/subjects/")
def get_subjects():
    subjects = models.Subject.query.order_by(asc(models.Subject.id)).all()
    return json.dumps([subject.name for subject in subjects])


@app.route("/subjects/<subject_name>/", methods=["DELETE"])
def delete_subject(subject_name: str) -> str:
    subject = models.Subject.query.filter(models.Subject.name == subject_name).first()
    if subject is None:
        abort(404)

    versions = json.dumps([version.version_id for version in subject.versions])

    db.session.delete(subject)
    db.session.commit()

    return versions


@app.route("/subjects/<subject_name>/", methods=["POST"])
def check_subject_schema(subject_name: str) -> str:
    subject = models.Subject.query.filter(models.Subject.name == subject_name).first()
    if subject is None:
        abort(404)

    data = request.get_json()

    if "schema" not in data:
        abort(400)

    schema = data["schema"]
    schema_type_name: str = data.get("schemaType", "AVRO")
    if schema_type_name not in models.SchemaType:
        abort(400)

    schema_type = models.SchemaType[schema_type_name]

    references: list[dict] = data.get("references", [])
    reference_names = set(
        [f"{reference['subject']}/{reference['version']}" for reference in references]
    )

    version = models.SubjectVersion.query.filter(
        models.SubjectVersion.schema == schema
        and models.SubjectVersion.schema_type == schema_type
    ).first()

    if version is None:
        abort(404)

    version_reference_names = set(
        [
            f"{reference['subject']}/{reference['version']}"
            for reference in version.references
        ]
    )
    if reference_names != version_reference_names:
        abort(404)

    return json.dumps(
        {
            "subject": version.subject.name,
            "id": version.id,
            "version": version.version_id,
            "schema": version.schema,
        }
    )


@app.route("/subjects/<subject_name>/versions/")
def get_subject_versions(subject_name: str) -> str:
    subject = models.Subject.query.filter(models.Subject.name == subject_name).first()
    if subject is None:
        abort(404)

    return json.dumps([version.version_id for version in subject.versions])


@app.route("/subjects/<subject_name>/versions/", methods=["POST"])
def create_subject_version(subject_name: str) -> str:
    subject = models.Subject.query.filter(models.Subject.name == subject_name).first()
    if subject is None:
        subject = models.Subject(name=subject_name)
        db.session.add(subject)

    json_data = request.get_json()

    if "schema" not in json_data or not json_data["schema"]:
        abort(400)
    schema: str = json_data["schema"]

    schema_type_name: str = json_data.get("schemaType", "AVRO")
    if models.SchemaType[schema_type_name] is None:
        abort(400)

    schema_type = models.SchemaType[schema_type_name]

    references: list[dict] = json_data.get("references", [])

    reference_subjects = models.Subject.query.filter(
        models.Subject.name in [reference["subject"] for reference in references]
    ).all()

    reference_names = [
        f"{reference['subject']}/{reference['version']}" for reference in references
    ]
    reference_versions = (
        models.SubjectVersion.query.join(
            models.Subject, models.SubjectVersion.subject_id == models.Subject.id
        )
        .filter(
            models.SubjectVersion.subject_id
            in [subject.id for subject in reference_subjects]
        )
        .all()
    )
    reference_versions = [
        version
        for version in reference_versions
        if f"{version.subject.name}/{version.version_id}" in reference_names
    ]
    if len(reference_versions) != len(references):
        abort(400)

    subject_versions = subject.versions
    if not subject_versions:
        next_version = 1
    else:
        next_version = max(version.version_id for version in subject.versions) + 1

    new_version = models.SubjectVersion(
        version_id=next_version,
        schema_type=schema_type,
        schema=schema,
        subject=subject,
        references=reference_versions,
    )
    db.session.add(new_version)
    db.session.commit()

    return json.dumps(
        {
            "id": subject.id,
        }
    )


@app.route("/subjects/<subject_name>/versions/<int:version_id>/")
def get_subject_version(subject_name: str, version_id: int) -> str:
    version = (
        models.SubjectVersion.query.join(
            models.Subject, models.SubjectVersion.subject_id == models.Subject.id
        )
        .filter(
            models.Subject.name == subject_name
            and models.SubjectVersion.version_id == version_id
        )
        .first()
    )

    if version is None:
        abort(404)

    reference_names = [reference.unique_name() for reference in version.references]

    return json.dumps(
        {
            "subject": version.subject.name,
            "id": version.id,
            "version": version.version_id,
            "schemaType": version.schema_type.name,
            "schema": version.schema,
            "references": reference_names,
        }
    )


@app.route("/subjects/<subject_name>/versions/<int:version_id>/referencedby/")
def get_subject_version_referencedby(subject_name: str, version_id: int) -> str:
    version = (
        models.SubjectVersion.query.join(
            models.Subject, models.SubjectVersion.subject_id == models.Subject.id
        )
        .filter(
            models.Subject.name == subject_name
            and models.SubjectVersion.version_id == version_id
        )
        .first()
    )

    if version is None:
        abort(404)

    return json.dumps([referer.id for referer in version.referrers])


@app.route("/subjects/<subject_name>/versions/<int:version_id>/schema/")
def get_subject_version_schema(subject_name: str, version_id: int) -> str:
    version = (
        models.SubjectVersion.query.join(
            models.Subject, models.SubjectVersion.subject_id == models.Subject.id
        )
        .filter(
            models.Subject.name == subject_name
            and models.SubjectVersion.version_id == version_id
        )
        .first()
    )

    if version is None:
        abort(404)

    return version.schema


if __name__ == "__main__":
    app.run()
