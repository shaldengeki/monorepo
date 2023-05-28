from ..config import db
import datetime


class UserActivity(db.Model):  # type: ignore
    __tablename__ = "user_activities"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    updated_at = db.Column(
        db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    record_date = db.Column(db.DATE, default=datetime.date.today, nullable=False)
    user = db.Column(db.Unicode(500), nullable=False)
    steps = db.Column(db.Integer, nullable=False)
    active_minutes = db.Column(db.Integer, nullable=False)
    distance_km = db.Column(db.DECIMAL(5, 2), nullable=False)

    def __repr__(self) -> str:
        return "<UserActivity {id}>".format(id=self.id)
