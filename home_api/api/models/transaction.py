from home_api.config import db


class Transaction(db.Model):
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
