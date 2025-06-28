import datetime
from typing import TYPE_CHECKING

from proto_registry.config import db


# SQLAlchemy defines the db.Model type dynamically, which doesn't work with mypy.
# We therefore import it explicitly in the typechecker, so this resolves.
if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model
else:
    Model = db.Model


class Subject(Model):
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
