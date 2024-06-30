from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fitbit_challenges.config import db


class FitbitSubscription(db.Model):
    __tablename__ = "fitbit_subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    fitbit_user_id: Mapped[str] = mapped_column(ForeignKey("users.fitbit_user_id"))
    user: Mapped["User"] = relationship(back_populates="fitbit_subscription")

    def __repr__(self) -> str:
        return "<FitbitSubscription {fitbit_user_id}>".format(
            fitbit_user_id=self.fitbit_user_id
        )
