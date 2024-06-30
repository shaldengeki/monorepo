import dataclasses
import datetime
import decimal
import enum
import itertools
import random
from typing import Generator, Optional

import requests
from sqlalchemy import ForeignKey, desc
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.functions import now

from fitbit_challenges.bingo_card_pattern import USABLE_PATTERNS, BingoCardPattern
from fitbit_challenges.config import db
from fitbit_challenges.fitbit_client import FitbitClient
from fitbit_challenges.models.challenge import Challenge
from fitbit_challenges.models.fitbit_subscription import FitbitSubscription
from fitbit_challenges.models.subscription_notification import SubscriptionNotification
from fitbit_challenges.total_amounts import TotalAmounts


class ChallengeMembership(db.Model):  # type: ignore
    __tablename__ = "challenge_memberships"
    fitbit_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.fitbit_user_id"), primary_key=True
    )
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id"), primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="challenge_memberships")
    challenge: Mapped["Challenge"] = relationship(back_populates="user_memberships")


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
        return f"<UserActivity {self.id} created_at={self.created_at} record_date={self.record_date}>"


def apply_fuzz_factor_to_int(
    amount: int, percentage: int, random_factor: Optional[int] = None
) -> int:
    if random_factor is None:
        random_factor = random.randint(-100 * percentage, 100 * percentage)
    else:
        random_factor *= 100

    fuzz_factor = 1 + (float(random_factor) / (100 * 100))
    return int(amount * fuzz_factor) or 1


def apply_fuzz_factor_to_decimal(
    amount: decimal.Decimal, percentage: int, random_factor: Optional[int] = None
) -> decimal.Decimal:
    if random_factor is None:
        random_factor = random.randint(-1 * percentage, percentage)

    fuzz_factor = decimal.Decimal(1) + (
        decimal.Decimal(random_factor) / decimal.Decimal(100)
    )

    return amount * fuzz_factor or decimal.Decimal(1)


@dataclasses.dataclass
class UnusedAmounts:
    steps: Optional[int]
    activeMinutes: Optional[int]
    distanceKm: Optional[decimal.Decimal]


class BingoTileBonusType(enum.Enum):
    STEPS = 0
    ACTIVE_MINUTES = 1
    DISTANCE_KM = 2
    HALVE = 3


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
    challenge: Mapped["Challenge"] = relationship(back_populates="bingo_cards")
    bingo_tiles: Mapped[list["BingoTile"]] = relationship(
        back_populates="bingo_card",
        order_by="(BingoTile.coordinate_y, BingoTile.coordinate_x)",
    )

    PATTERNS: list[BingoCardPattern] = [
        pattern_class() for pattern_class in USABLE_PATTERNS
    ]

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

    def victory_tiles(self) -> Generator["BingoTile", None, None]:
        for tile in self.bingo_tiles:
            if tile.required_for_win:
                yield tile

    def non_victory_tiles(self) -> Generator["BingoTile", None, None]:
        for tile in self.bingo_tiles:
            if not tile.required_for_win:
                yield tile

    def flipped_victory_tiles(self) -> Generator["BingoTile", None, None]:
        for tile in self.victory_tiles():
            if tile.flipped:
                yield tile

    def unflipped_victory_tiles(self) -> Generator["BingoTile", None, None]:
        for tile in self.victory_tiles():
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

    def assign_bonus_tiles(self, totals: TotalAmounts) -> None:
        non_victory_tiles = []
        step_tiles = 0
        minutes_tiles = 0
        distance_tiles = 0
        for tile in self.non_victory_tiles():
            non_victory_tiles.append(tile)
            if tile.steps is not None:
                step_tiles += 1
            elif tile.active_minutes is not None:
                minutes_tiles += 1
            elif tile.distance_km is not None:
                distance_tiles += 1

        non_victory_tiles = list(self.non_victory_tiles())
        random.shuffle(non_victory_tiles)

        totals = totals.copy()
        average_per_tile = TotalAmounts(
            steps=int(round(totals.steps / (step_tiles or 1), 0)),
            active_minutes=int(round(totals.active_minutes / (minutes_tiles or 1), 0)),
            distance_km=totals.distance_km / (distance_tiles or 1),
        )

        for idx, tile in enumerate(non_victory_tiles):
            if idx % 2 != 0:
                # only make half the tiles bonus tiles.
                continue

            # Pick a resource other than the one this tile cost to assign a bonus for.
            if tile.steps is not None:
                bonus_type = random.choice(
                    [
                        BingoTileBonusType.ACTIVE_MINUTES,
                        BingoTileBonusType.DISTANCE_KM,
                        BingoTileBonusType.HALVE,
                    ]
                )
            elif tile.active_minutes is not None:
                bonus_type = random.choice(
                    [
                        BingoTileBonusType.STEPS,
                        BingoTileBonusType.DISTANCE_KM,
                        BingoTileBonusType.HALVE,
                    ]
                )
            elif tile.distance_km is not None:
                bonus_type = random.choice(
                    [
                        BingoTileBonusType.STEPS,
                        BingoTileBonusType.ACTIVE_MINUTES,
                        BingoTileBonusType.HALVE,
                    ]
                )

            tile.bonus_type = bonus_type.value
            amount: Optional[int | decimal.Decimal]

            if bonus_type == BingoTileBonusType.STEPS:
                amount = apply_fuzz_factor_to_int(average_per_tile.steps, 20)
                if amount > totals.steps:
                    amount = totals.steps
                totals.steps -= amount
            elif bonus_type == BingoTileBonusType.ACTIVE_MINUTES:
                amount = apply_fuzz_factor_to_int(average_per_tile.active_minutes, 20)
                if amount > totals.active_minutes:
                    amount = totals.active_minutes
                totals.active_minutes -= amount
            elif bonus_type == BingoTileBonusType.DISTANCE_KM:
                amount = apply_fuzz_factor_to_decimal(average_per_tile.distance_km, 20)
                if amount > totals.distance_km:
                    amount = totals.distance_km
                totals.distance_km -= amount
            elif bonus_type == BingoTileBonusType.HALVE:
                amount = None
            else:
                raise ValueError(f"Unknown bonus type: {bonus_type}")

            if amount is not None:
                tile.bonus_amount = int(amount)

    def compute_total_amounts_for_resource(
        self,
        user: User,
        start: datetime.datetime,
        end: datetime.datetime,
        pattern: BingoCardPattern,
    ) -> TotalAmounts:
        # Compute the total amounts for each resource.
        duration = end - start
        duration_days = float(duration.total_seconds()) / 86400

        # Get the user's average activity over the last 30d.
        window_start = start - datetime.timedelta(days=30)

        total_steps = 0
        total_active_minutes = 0
        total_distance_km: decimal.Decimal = decimal.Decimal(0)

        for activity in user.latest_activity_for_days_within_timespan(
            start=window_start, end=start
        ):
            total_steps += activity.steps
            total_active_minutes += activity.active_minutes
            total_distance_km += activity.distance_km

        # Compute average daily activity over this period.
        average_steps = float(total_steps) / 30
        average_active_minutes = float(total_active_minutes) / 30
        average_distance_km = total_distance_km / 30

        expected_steps = decimal.Decimal(average_steps * duration_days)
        expected_active_minutes = decimal.Decimal(
            average_active_minutes * duration_days
        )
        expected_distance_km = average_distance_km * decimal.Decimal(duration_days)

        victory_tile_proportion = decimal.Decimal(
            pattern.number_of_required_tiles
        ) / decimal.Decimal(pattern.number_of_tiles)
        total_steps = int(round(expected_steps / victory_tile_proportion, 0))
        total_active_minutes = int(
            round(expected_active_minutes / victory_tile_proportion, 0)
        )
        total_distance_km = decimal.Decimal(
            round(expected_distance_km / victory_tile_proportion, 2)
        )

        return TotalAmounts(
            steps=total_steps,
            active_minutes=total_active_minutes,
            distance_km=total_distance_km,
        )

    def create_for_user_and_challenge(
        self,
        user: User,
        challenge: "Challenge",
        start: datetime.datetime,
        end: datetime.datetime,
        pattern: Optional[BingoCardPattern] = None,
    ) -> "BingoCard":
        # Assign this card to the user and challenge.
        self.user = user
        self.challenge = challenge

        # Hard code the rows & cols.
        self.rows = 5
        self.columns = 5

        if pattern is None:
            # Pick one of a set of victory patterns.
            pattern = random.choice(BingoCard.PATTERNS)

        total_amounts = self.compute_total_amounts_for_resource(
            user, start, end, pattern
        )

        # Create 25=5x5 tiles.
        step_tiles = [BingoTile(bingo_card=self) for _ in range(random.randint(7, 9))]
        active_minutes_tiles = [
            BingoTile(bingo_card=self) for _ in range(random.randint(7, 9))
        ]
        distance_km_tiles = [
            BingoTile(bingo_card=self)
            for _ in range(25 - len(step_tiles) - len(active_minutes_tiles))
        ]

        # Create a random ordering of tile coordinates.
        coordinates = list(
            itertools.product(
                list(range(5)),
                list(range(5)),
            )
        )
        random.shuffle(coordinates)

        for step_tile in step_tiles:
            # Assign ~1/8 or ~1/9 of the total resource amount
            step_tile.steps = apply_fuzz_factor_to_int(
                int(total_amounts.steps / len(step_tiles)), 20
            )

            # Assign a coordinate
            (step_tile.coordinate_x, step_tile.coordinate_y) = coordinates.pop()

            # Set whether or not it's required for a win.
            step_tile.required_for_win = pattern.required_coordinate(
                x=step_tile.coordinate_x, y=step_tile.coordinate_y
            )

        for active_minutes_tile in active_minutes_tiles:
            # Assign ~1/8 or ~1/9 of the total resource amount
            active_minutes_tile.active_minutes = apply_fuzz_factor_to_int(
                int(total_amounts.active_minutes / len(active_minutes_tiles)), 20
            )

            # Assign a coordinate
            (
                active_minutes_tile.coordinate_x,
                active_minutes_tile.coordinate_y,
            ) = coordinates.pop()

            # Set whether or not it's required for a win.
            active_minutes_tile.required_for_win = pattern.required_coordinate(
                x=active_minutes_tile.coordinate_x, y=active_minutes_tile.coordinate_y
            )

        for distance_km_tile in distance_km_tiles:
            # Assign ~1/8 or ~1/9 of the total resource amount
            distance_km_tile.distance_km = apply_fuzz_factor_to_decimal(
                total_amounts.distance_km / len(distance_km_tiles), 20
            )

            # Assign a coordinate
            (
                distance_km_tile.coordinate_x,
                distance_km_tile.coordinate_y,
            ) = coordinates.pop()

            # Set whether or not it's required for a win.
            distance_km_tile.required_for_win = pattern.required_coordinate(
                x=distance_km_tile.coordinate_x, y=distance_km_tile.coordinate_y
            )

        self.bingo_tiles = step_tiles + active_minutes_tiles + distance_km_tiles

        # assign bonus tiles.
        self.assign_bonus_tiles(
            TotalAmounts(
                steps=int(round(total_amounts.steps / 10, 0)),
                active_minutes=int(round(total_amounts.active_minutes / 10, 0)),
                distance_km=total_amounts.distance_km / 10,
            )
        )

        return self

    def unused_amounts(self) -> UnusedAmounts:
        # Sum up the total user's resources.
        total_steps = 0
        total_active_minutes = 0
        total_distance_km = decimal.Decimal(0)
        for activity in self.challenge.latest_activities_per_day_for_user(self.user):
            total_steps += activity.steps
            total_active_minutes += activity.active_minutes
            total_distance_km += activity.distance_km

        for tile in self.flipped_tiles():
            # Subtract out the user's used steps.
            if tile.steps is not None:
                total_steps -= tile.steps
            if tile.active_minutes is not None:
                total_active_minutes -= tile.active_minutes
            if tile.distance_km is not None:
                total_distance_km -= tile.distance_km
            # Add in any bonuses.
            if tile.bonus_type is not None and tile.bonus_amount is not None:
                if tile.bonus_type == BingoTileBonusType.STEPS.value:
                    total_steps += tile.bonus_amount
                elif tile.bonus_type == BingoTileBonusType.ACTIVE_MINUTES.value:
                    total_active_minutes += tile.bonus_amount
                elif tile.bonus_type == BingoTileBonusType.DISTANCE_KM.value:
                    total_distance_km += decimal.Decimal(
                        tile.bonus_amount
                    ) / decimal.Decimal("100.00")

        return UnusedAmounts(
            steps=total_steps,
            activeMinutes=total_active_minutes,
            distanceKm=total_distance_km,
        )

    def unfinished(self) -> bool:
        return any(t for t in self.unflipped_victory_tiles())

    def finished(self) -> bool:
        return not any(t for t in self.unflipped_victory_tiles())

    def finished_at(self) -> Optional[datetime.datetime]:
        max_flipped_at = datetime.datetime(
            year=1,
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            tzinfo=datetime.timezone.utc,
        )
        victory_tiles = 0
        for t in self.victory_tiles():
            victory_tiles += 1
            if not t.flipped or t.flipped_at is None:
                return None
            if t.flipped_at > max_flipped_at:
                max_flipped_at = t.flipped_at

        if victory_tiles == 0:
            return None

        return max_flipped_at


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

    def flip(self) -> bool:
        if self.flipped:
            return self.flipped

        self.flipped = True
        self.flipped_at = datetime.datetime.now(tz=datetime.timezone.utc)
        return self.flipped
