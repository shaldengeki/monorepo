import datetime
from typing import Generator, Optional

import requests
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import now

from fitbit_challenges.config import db
from fitbit_challenges.fitbit_client import FitbitClient
from fitbit_challenges.models import (
    BingoCard,
    ChallengeMembership,
    SubscriptionNotification,
    UserActivity,
)
from fitbit_challenges.models.challenge import Challenge
from fitbit_challenges.models.fitbit_subscription import FitbitSubscription


class User(db.Model):
    __tablename__ = "users"

    fitbit_user_id: Mapped[str] = mapped_column(db.Unicode(100), primary_key=True)
    display_name: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )
    fitbit_access_token: Mapped[str]
    fitbit_refresh_token: Mapped[str]
    synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        db.TIMESTAMP(timezone=True), nullable=True
    )

    fitbit_subscription: Mapped["FitbitSubscription"] = relationship(
        back_populates="user"
    )
    subscription_notifications: Mapped[list["SubscriptionNotification"]] = relationship(
        back_populates="user"
    )
    activities: Mapped[list["UserActivity"]] = relationship(
        back_populates="fitbit_user"
    )
    bingo_cards: Mapped[list["BingoCard"]] = relationship(back_populates="user")

    challenges: Mapped[list["Challenge"]] = relationship(
        secondary="challenge_memberships", back_populates="users", viewonly=True
    )
    challenge_memberships: Mapped[list["ChallengeMembership"]] = relationship(
        back_populates="user"
    )

    def __repr__(self) -> str:
        return "<User {fitbit_user_id}>".format(fitbit_user_id=self.fitbit_user_id)

    @staticmethod
    def fetch_display_name_with_user_id_and_access_token(
        user_id: str, access_token: str
    ) -> str:
        profile_request = requests.get(
            f"https://api.fitbit.com/1/user/{user_id}/profile.json",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )
        return profile_request.json()["user"]["displayName"]

    def fetch_display_name(self) -> str:
        return self.__class__.fetch_display_name_with_user_id_and_access_token(
            self.fitbit_user_id, self.fitbit_access_token
        )

    @classmethod
    def create_with_user_id_and_tokens(
        cls, user_id: str, access_token: str, refresh_token: str
    ):
        display_name = cls.fetch_display_name_with_user_id_and_access_token(
            user_id, access_token
        )
        return (
            insert(cls.__table__)
            .values(
                fitbit_user_id=user_id,
                display_name=display_name,
                fitbit_access_token=access_token,
                fitbit_refresh_token=refresh_token,
            )
            .on_conflict_do_update(
                constraint="users_pkey",
                set_={
                    "display_name": display_name,
                    "fitbit_access_token": access_token,
                    "fitbit_refresh_token": refresh_token,
                },
            )
        )

    def create_subscription(
        self, client: FitbitClient
    ) -> Optional["FitbitSubscription"]:
        if self.fitbit_subscription is not None:
            return self.fitbit_subscription

        new_subscription = FitbitSubscription(fitbit_user_id=self.fitbit_user_id)
        db.session.add(new_subscription)
        db.session.commit()

        if not client.create_subscription(
            self.fitbit_user_id, new_subscription.id, self.fitbit_access_token
        ):
            db.session.delete(new_subscription)
            db.session.commit()
            return None

        return new_subscription

    def challenges_query(self):
        return Challenge.query.filter(
            Challenge.id.in_(
                membership.challenge_id for membership in self.challenge_memberships
            )
        )

    def past_challenges(self) -> list["Challenge"]:
        return self.challenges_query().filter(Challenge.end_at < now()).all()

    def active_challenges(self) -> list["Challenge"]:
        return self.challenges_query().filter(Challenge.end_at >= now()).all()

    def activities_within_timespan(
        self, start: datetime.datetime, end: datetime.datetime
    ) -> list["UserActivity"]:
        filtered_activities = [
            activity
            for activity in self.activities
            if activity.created_at >= start and activity.created_at < end
        ]
        return sorted(filtered_activities, key=lambda a: [a.record_date, a.created_at])

    def latest_activity_for_days_within_timespan(
        self, start: datetime.datetime, end: datetime.datetime
    ) -> Generator["UserActivity", None, None]:
        prev_activity = None
        activity = None
        for activity in self.activities_within_timespan(start, end):
            if (
                prev_activity is not None
                and activity.record_date > prev_activity.record_date
            ):
                yield prev_activity
            prev_activity = activity

        if activity is not None:
            yield activity

    def last_activity(self) -> Optional["UserActivity"]:
        if not self.activities:
            return None

        return max(self.activities, key=lambda a: a.created_at)
