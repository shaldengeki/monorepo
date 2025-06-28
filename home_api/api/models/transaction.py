from home_api.config import db
from typing import TYPE_CHECKING


# SQLAlchemy defines the db.Model type dynamically, which doesn't work with mypy.
# We therefore import it explicitly in the typechecker, so this resolves.
if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model
else:
    Model = db.Model


class Transaction(Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    description = db.Column(db.Unicode(500), nullable=False)
    original_description = db.Column(db.Unicode(500), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Unicode(100), nullable=False)
    category = db.Column(db.Unicode(100), nullable=False)
    account = db.Column(db.Unicode(100), nullable=False)
    labels = db.Column(db.Unicode(500), nullable=True)
    notes = db.Column(db.Unicode(500), nullable=True)

    def __repr__(self):
        return "<Transaction {id}>".format(id=self.id)
