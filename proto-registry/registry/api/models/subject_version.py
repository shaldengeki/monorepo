from ..config import db
from .subject import Subject
from sqlalchemy import Enum
import datetime
import enum
import json

class SchemaType(enum.Enum):
    AVRO = 1
    PROTOBUF = 2
    JSONSCHEMA = 3

subject_version_reference_table = db.Table(
    "subject_version_references",
    db.Column("referrer_id", db.Integer, db.ForeignKey("subject_versions.id"), primary_key=True),
    db.Column("referred_id", db.Integer, db.ForeignKey("subject_versions.id"), primary_key=True),
)

class SubjectVersion(db.Model):
    __tablename__ = "subject_versions"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(
        db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    version_id = db.Column(db.Integer, nullable=False)
    schema_type = db.Column(Enum(SchemaType), nullable=True, default=SchemaType.AVRO)
    schema = db.Column(db.Unicode(20000), nullable=False)

    references = db.relationship(
        "SubjectVersion",
        secondary=subject_version_reference_table,
        primaryjoin=id==subject_version_reference_table.c.referrer_id,
        secondaryjoin=id==subject_version_reference_table.c.referred_id,
        lazy="subquery",
        backref=db.backref("referrers", lazy=True),
    )

    subject_id = db.Column(db.Integer, db.ForeignKey(Subject.id), nullable=False)
    subject = db.relationship(
        "Subject", back_populates="versions", order_by="desc(SubjectVersion.version_id)"
    )

    def __repr__(self):
        return "<Server {id}>".format(id=self.id)

    def __dict__(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_json(self):
        return json.dumps(dict(self))

    def unique_name(self):
        return f"{self.subject.name}/{self.version_id}"