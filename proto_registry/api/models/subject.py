import datetime

from proto_registry.config import db


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(
        db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    name = db.Column(db.Unicode(2000), nullable=False, unique=True)
    versions = db.relationship(
        "SubjectVersion",
        back_populates="subject",
        order_by="desc(SubjectVersion.version_id)",
    )

    def __repr__(self):
        return f"<Subject name={self.name}>"
