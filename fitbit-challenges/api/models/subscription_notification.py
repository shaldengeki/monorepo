from ..config import db
import datetime


class SubscriptionNotification(db.Model):  # type: ignore
    __tablename__ = "subscription_notifications"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    processed_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    collection_type = db.Column(
        db.Unicode(100),
        nullable=False,
    )
    date = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    fitbit_user_id = db.Column(db.Unicode(100), nullable=False)

    def __repr__(self) -> str:
        return "<SubscriptionNotification {id}>".format(id=self.id)
