import datetime
import decimal
import enum
from typing import Generator

from sqlalchemy import desc
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from fitbit_challenges.config import db
from fitbit_challenges.models import UserActivity
from fitbit_challenges.models.user import User
from fitbit_challenges.total_amounts import TotalAmounts


class ChallengeType(enum.Enum):
    WORKWEEK_HUSTLE = 0
    WEEKEND_WARRIOR = 1
    BINGO = 2


class Challenge(db.Model):
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(primary_key=True)
    challenge_type: Mapped[int]
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )
    start_at: Mapped[datetime.datetime] = mapped_column(db.TIMESTAMP(timezone=True))
    end_at: Mapped[datetime.datetime] = mapped_column(db.TIMESTAMP(timezone=True))

    bingo_cards: Mapped[list["BingoCard"]] = relationship(back_populates="challenge")

    users: Mapped[list["User"]] = relationship(
        secondary="challenge_memberships", back_populates="challenges", viewonly=True
    )

    user_memberships: Mapped[list["ChallengeMembership"]] = relationship(
        back_populates="challenge"
    )

    def __repr__(self) -> str:
        return "<Challenge {id}>".format(id=self.id)

    @property
    def started(self) -> bool:
        return datetime.datetime.now(tz=datetime.timezone.utc) >= self.start_at

    @property
    def ended(self) -> bool:
        return datetime.datetime.now(tz=datetime.timezone.utc) >= self.end_at

    @property
    def seal_at(self) -> datetime.datetime:
        if self.challenge_type in (
            ChallengeType.WEEKEND_WARRIOR.value,
            ChallengeType.WORKWEEK_HUSTLE.value,
        ):
            return self.end_at + datetime.timedelta(hours=24)
        elif self.challenge_type == ChallengeType.BINGO.value:
            return self.end_at
        else:
            raise ValueError(f"Invalid challenge type: {self.challenge_type}")

    @property
    def sealed(self) -> bool:
        return datetime.datetime.now(tz=datetime.timezone.utc) >= self.seal_at

    @property
    def users_list(self) -> list["User"]:
        user_ids = [user.fitbit_user_id for user in self.users]
        return (
            User.query.filter(User.fitbit_user_id.in_(user_ids))
            .order_by(User.display_name)
            .all()
        )

    def activities(self) -> list["UserActivity"]:
        return (
            UserActivity.query.filter(
                UserActivity.user.in_(
                    membership.fitbit_user_id for membership in self.user_memberships
                )
            )
            .filter(
                func.date_trunc("day", UserActivity.record_date)
                >= func.date_trunc("day", self.start_at)
            )
            .filter(UserActivity.record_date < self.end_at)
            .filter(UserActivity.created_at < self.seal_at)
            .order_by(desc(UserActivity.created_at))
            .all()
        )

    def activities_for_user(self, user: "User") -> list["UserActivity"]:
        return (
            UserActivity.query.filter(UserActivity.user == user.fitbit_user_id)
            .filter(
                func.date_trunc("day", UserActivity.record_date)
                >= func.date_trunc("day", self.start_at)
            )
            .filter(UserActivity.record_date < self.end_at)
            .order_by(desc(UserActivity.created_at))
            .all()
        )

    def latest_activities_per_day_for_user(
        self, user: "User"
    ) -> Generator["UserActivity", None, None]:
        for activity in user.latest_activity_for_days_within_timespan(
            self.start_at, self.seal_at
        ):
            if activity.record_date > self.end_at.date():
                continue
            if activity.record_date < self.start_at.date():
                continue
            yield activity

    def total_amounts(self) -> dict["User", "TotalAmounts"]:
        total_amounts = {}
        for user in self.users:
            total_amounts[user] = TotalAmounts(
                steps=0, active_minutes=0, distance_km=decimal.Decimal(0.0)
            )
            for activity in self.latest_activities_per_day_for_user(user):
                total_amounts[user].steps += activity.steps
                total_amounts[user].active_minutes += activity.active_minutes
                total_amounts[user].distance_km += activity.distance_km

        return total_amounts
