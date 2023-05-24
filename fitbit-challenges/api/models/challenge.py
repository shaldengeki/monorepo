from ..config import db
import datetime
from datetime import timezone


class Challenge(db.Model):  # type: ignore
    __tablename__ = "challenges"
    id = db.Column(db.Integer, primary_key=True)
    challenge_type = db.Column(db.Integer, nullable=False)
    users = db.Column(db.Unicode(500), nullable=False)
    created_at = db.Column(
        db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    start_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    end_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return "<Challenge {id}>".format(id=self.id)

    @property
    def ended(self) -> bool:
        return datetime.datetime.now() >= self.end_at

    @property
    def seal_at(self) -> datetime.datetime:
        return self.end_at + datetime.timedelta(hours=24)

    @property
    def sealed(self) -> bool:
        return datetime.datetime.now() >= self.seal_at
