from ..config import db
import datetime
import json


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(
        db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    name = db.Column(db.Unicode(2000), nullable=False, unique=True)
    versions = db.relationship(
        "SubjectVersion", back_populates="subject", order_by="desc(SubjectVersion.version_id)"
    )

    def __repr__(self):
        return "<Server {id}>".format(id=self.id)

    def __dict__(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_json(self):
        return json.dumps(dict(self))