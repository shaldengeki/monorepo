from ..config import db
import datetime


class User(db.Model):  # type: ignore
    __tablename__ = "users"
    fitbit_user_id = db.Column(db.Unicode(100), primary_key=True)
    display_name = db.Column(db.Unicode(100), nullable=True)
    created_at = db.Column(
        db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    fitbit_access_token = db.Column(db.Unicode(100), nullable=False)
    fitbit_refresh_token = db.Column(db.Unicode(100), nullable=False)
    synced_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return "<User {fitbit_user_id}>".format(fitbit_user_id=self.fitbit_user_id)
