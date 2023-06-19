import datetime
import decimal
import requests
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import mapped_column
from typing import Generator, Optional

from .config import db
from .fitbit_client import FitbitClient


class Challenge(db.Model):  # type: ignore
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(primary_key=True)
    challenge_type: Mapped[int]
    users: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )
    start_at: Mapped[datetime.datetime] = mapped_column(db.TIMESTAMP(timezone=True))
    end_at: Mapped[datetime.datetime] = mapped_column(db.TIMESTAMP(timezone=True))

    bingo_card: Mapped["BingoCard"] = relationship(back_populates="challenge")

    def __repr__(self) -> str:
        return "<Challenge {id}>".format(id=self.id)

    @property
    def ended(self) -> bool:
        return datetime.datetime.now(tz=datetime.timezone.utc) >= self.end_at

    @property
    def seal_at(self) -> datetime.datetime:
        return self.end_at + datetime.timedelta(hours=24)

    @property
    def sealed(self) -> bool:
        return datetime.datetime.now(tz=datetime.timezone.utc) >= self.seal_at


class FitbitSubscription(db.Model):  # type: ignore
    __tablename__ = "fitbit_subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    fitbit_user_id: Mapped[str] = mapped_column(ForeignKey("users.fitbit_user_id"))
    user: Mapped["User"] = relationship(back_populates="fitbit_subscription")

    def __repr__(self) -> str:
        return "<FitbitSubscription {fitbit_user_id}>".format(
            fitbit_user_id=self.fitbit_user_id
        )


class SubscriptionNotification(db.Model):  # type: ignore
    __tablename__ = "subscription_notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )
    processed_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        db.TIMESTAMP(timezone=True)
    )
    collection_type: Mapped[str]
    date: Mapped[datetime.datetime] = mapped_column(db.TIMESTAMP(timezone=True))
    fitbit_user_id: Mapped[str] = mapped_column(ForeignKey("users.fitbit_user_id"))

    user: Mapped["User"] = relationship(back_populates="subscription_notifications")

    def __repr__(self) -> str:
        return "<SubscriptionNotification {id}>".format(id=self.id)


class User(db.Model):  # type: ignore
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


class UserActivity(db.Model):  # type: ignore
    __tablename__ = "user_activities"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )
    record_date: Mapped[datetime.date] = mapped_column(
        db.DATE, default=datetime.date.today
    )
    user: Mapped[str] = mapped_column(ForeignKey("users.fitbit_user_id"))
    steps: Mapped[int]
    active_minutes: Mapped[int]
    distance_km: Mapped[decimal.Decimal] = mapped_column(db.DECIMAL(5, 2))

    fitbit_user: Mapped["User"] = relationship(back_populates="activities")

    def __repr__(self) -> str:
        return "<UserActivity {id}>".format(id=self.id)


class BingoCard(db.Model):  # type: ignore
    __tablename__ = "bingo_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    fitbit_user_id: Mapped[str] = mapped_column(ForeignKey("users.fitbit_user_id"))
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id"))
    rows: Mapped[int]
    columns: Mapped[int]
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="bingo_cards")
    challenge: Mapped["Challenge"] = relationship(back_populates="bingo_card")
    bingo_tiles: Mapped[list["BingoTile"]] = relationship(
        back_populates="bingo_card",
        order_by="(BingoTile.coordinate_y, BingoTile.coordinate_x)",
    )

    def __repr__(self) -> str:
        return "<BingoCard {id}>".format(id=self.id)

    def flipped_tiles(self) -> Generator["BingoTile", None, None]:
        for tile in self.bingo_tiles:
            if tile.flipped:
                yield tile

    def unflipped_tiles(self) -> Generator["BingoTile", None, None]:
        for tile in self.bingo_tiles:
            if not tile.flipped:
                yield tile

    def total_cost_steps(self) -> int:
        return sum(tile.steps for tile in self.bingo_tiles if tile.steps is not None)

    def total_cost_active_minutes(self) -> int:
        return sum(
            tile.active_minutes
            for tile in self.bingo_tiles
            if tile.active_minutes is not None
        )

    def total_cost_distance_km(self) -> decimal.Decimal:
        return decimal.Decimal(
            sum(
                tile.distance_km
                for tile in self.bingo_tiles
                if tile.distance_km is not None
            )
        )


class BingoTile(db.Model):  # type: ignore
    __tablename__ = "bingo_tiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    bingo_card_id: Mapped[str] = mapped_column(ForeignKey("bingo_cards.id"))
    steps: Mapped[Optional[int]]
    active_minutes: Mapped[Optional[int]]
    distance_km: Mapped[Optional[decimal.Decimal]]
    coordinate_x: Mapped[int]
    coordinate_y: Mapped[int]
    bonus_type: Mapped[Optional[int]]
    bonus_amount: Mapped[Optional[int]]
    flipped: Mapped[bool] = mapped_column(default=False)
    flipped_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        db.TIMESTAMP(timezone=True)
    )
    required_for_win: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )

    bingo_card: Mapped["BingoCard"] = relationship(back_populates="bingo_tiles")

    def __repr__(self) -> str:
        return "<BingoTile {id}>".format(id=self.id)
