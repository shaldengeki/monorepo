from ..config import db
import datetime


class WorkweekHustle(db.Model):  # type: ignore
    __tablename__ = "workweek_hustles"
    id = db.Column(db.Integer, primary_key=True)
    users = db.Column(db.Unicode(500), nullable=False)
    created_at = db.Column(
        db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    start_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    end_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return "<WorkweekHustle {id}>".format(id=self.id)
