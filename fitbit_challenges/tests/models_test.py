import datetime
import decimal
from typing import Generator

from fitbit_challenges.models import (
    BingoCard,
    BingoCardPattern,
    BingoTile,
    BingoTileBonusType,
    Challenge,
    ChallengeType,
    TotalAmounts,
    User,
    UserActivity,
    apply_fuzz_factor_to_decimal,
    apply_fuzz_factor_to_int,
)


def create_mock_datetime(returned_date: datetime.datetime) -> object:
    class MockDateTime(datetime.datetime):
        @classmethod
        def now(cls, *args, **kwargs):
            return returned_date

    return MockDateTime


class TestChallenge:
    def test_ended_for_current_second(self, monkeypatch):
        challenge = Challenge(
            end_at=datetime.datetime(
                year=2023,
                month=2,
                day=2,
                hour=0,
                minute=0,
                second=0,
                tzinfo=datetime.timezone.utc,
            )
        )
        monkeypatch.setattr(
            datetime,
            "datetime",
            create_mock_datetime(
                datetime.datetime(2023, 2, 2, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
        )
        assert challenge.ended

    def test_ended_for_prior_time(self, monkeypatch):
        challenge = Challenge(
            end_at=datetime.datetime(
                year=2023,
                month=2,
                day=2,
                hour=0,
                minute=0,
                second=0,
                tzinfo=datetime.timezone.utc,
            )
        )
        monkeypatch.setattr(
            datetime,
            "datetime",
            create_mock_datetime(
                datetime.datetime(2023, 2, 3, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
        )
        assert challenge.ended

    def test_ended_for_future_time(self, monkeypatch):
        challenge = Challenge(
            end_at=datetime.datetime(
                year=2023,
                month=2,
                day=2,
                hour=0,
                minute=0,
                second=0,
                tzinfo=datetime.timezone.utc,
            )
        )
        monkeypatch.setattr(
            datetime,
            "datetime",
            create_mock_datetime(
                datetime.datetime(2023, 2, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
        )
        assert not challenge.ended

    def test_total_amounts_with_no_users_returns_empty(self):
        c = Challenge(users=[])
        assert {} == c.total_amounts()

    def test_total_amounts_with_one_user_returns_total_amount(self):
        u1 = User(activities=[])
        c = Challenge(
            users=[u1],
            challenge_type=ChallengeType.WORKWEEK_HUSTLE.value,
            end_at=datetime.datetime.now(tz=datetime.timezone.utc),
        )
        assert {
            u1: TotalAmounts(
                steps=0, active_minutes=0, distance_km=decimal.Decimal(0.0)
            )
        } == c.total_amounts()

    def test_total_amounts_with_one_user_with_activity_returns_total(self):
        u1 = User(
            activities=[
                UserActivity(
                    created_at=datetime.datetime(
                        2020, 12, 2, tzinfo=datetime.timezone.utc
                    ),
                    record_date=datetime.date(2020, 12, 2),
                    steps=12,
                    active_minutes=23,
                    distance_km=decimal.Decimal("3.4"),
                )
            ]
        )
        c = Challenge(
            users=[u1],
            challenge_type=ChallengeType.WORKWEEK_HUSTLE.value,
            start_at=datetime.datetime(2020, 12, 1, tzinfo=datetime.timezone.utc),
            end_at=datetime.datetime(2020, 12, 3, tzinfo=datetime.timezone.utc),
        )
        assert {
            u1: TotalAmounts(
                steps=12, active_minutes=23, distance_km=decimal.Decimal("3.4")
            )
        } == c.total_amounts()

    def test_total_amounts_with_one_user_with_activities_returns_total(self):
        u1 = User(
            activities=[
                UserActivity(
                    created_at=datetime.datetime(
                        2020, 12, 2, tzinfo=datetime.timezone.utc
                    ),
                    record_date=datetime.date(2020, 12, 2),
                    steps=12,
                    active_minutes=23,
                    distance_km=decimal.Decimal("3.4"),
                ),
                UserActivity(
                    created_at=datetime.datetime(
                        2020, 12, 2, 1, tzinfo=datetime.timezone.utc
                    ),
                    record_date=datetime.date(2020, 12, 2),
                    steps=13,
                    active_minutes=24,
                    distance_km=decimal.Decimal("3.5"),
                ),
            ]
        )
        c = Challenge(
            users=[u1],
            challenge_type=ChallengeType.WORKWEEK_HUSTLE.value,
            start_at=datetime.datetime(2020, 12, 1, tzinfo=datetime.timezone.utc),
            end_at=datetime.datetime(2020, 12, 3, tzinfo=datetime.timezone.utc),
        )
        assert {
            u1: TotalAmounts(
                steps=13, active_minutes=24, distance_km=decimal.Decimal("3.5")
            )
        } == c.total_amounts()

    def test_total_amounts_with_one_user_with_multi_day_activities_returns_total(self):
        u1 = User(
            activities=[
                UserActivity(
                    created_at=datetime.datetime(
                        2020, 12, 2, tzinfo=datetime.timezone.utc
                    ),
                    record_date=datetime.date(2020, 12, 2),
                    steps=12,
                    active_minutes=23,
                    distance_km=decimal.Decimal("3.4"),
                ),
                UserActivity(
                    created_at=datetime.datetime(
                        2020, 12, 2, 1, tzinfo=datetime.timezone.utc
                    ),
                    record_date=datetime.date(2020, 12, 2),
                    steps=13,
                    active_minutes=24,
                    distance_km=decimal.Decimal("3.5"),
                ),
                UserActivity(
                    created_at=datetime.datetime(
                        2020, 12, 3, tzinfo=datetime.timezone.utc
                    ),
                    record_date=datetime.date(2020, 12, 3),
                    steps=25,
                    active_minutes=36,
                    distance_km=decimal.Decimal("4.7"),
                ),
            ]
        )
        c = Challenge(
            users=[u1],
            challenge_type=ChallengeType.WORKWEEK_HUSTLE.value,
            start_at=datetime.datetime(2020, 12, 1, tzinfo=datetime.timezone.utc),
            end_at=datetime.datetime(2020, 12, 4, tzinfo=datetime.timezone.utc),
        )
        assert {
            u1: TotalAmounts(
                steps=38, active_minutes=60, distance_km=decimal.Decimal("8.2")
            )
        } == c.total_amounts()

    def test_total_amounts_with_two_users_returns_total_amounts(self):
        u1 = User(activities=[])
        u2 = User(activities=[])
        c = Challenge(
            users=[u1, u2],
            challenge_type=ChallengeType.WORKWEEK_HUSTLE.value,
            end_at=datetime.datetime.now(tz=datetime.timezone.utc),
        )
        assert {
            u1: TotalAmounts(
                steps=0, active_minutes=0, distance_km=decimal.Decimal(0.0)
            ),
            u2: TotalAmounts(
                steps=0, active_minutes=0, distance_km=decimal.Decimal(0.0)
            ),
        } == c.total_amounts()

    def test_total_amounts_with_two_users_with_activity_returns_total(self):
        u1 = User(
            activities=[
                UserActivity(
                    created_at=datetime.datetime(
                        2020, 12, 2, tzinfo=datetime.timezone.utc
                    ),
                    record_date=datetime.date(2020, 12, 2),
                    steps=12,
                    active_minutes=23,
                    distance_km=decimal.Decimal("3.4"),
                )
            ]
        )
        u2 = User(
            activities=[
                UserActivity(
                    created_at=datetime.datetime(
                        2020, 12, 2, tzinfo=datetime.timezone.utc
                    ),
                    record_date=datetime.date(2020, 12, 2),
                    steps=24,
                    active_minutes=35,
                    distance_km=decimal.Decimal("4.6"),
                )
            ]
        )
        c = Challenge(
            users=[u1, u2],
            challenge_type=ChallengeType.WORKWEEK_HUSTLE.value,
            start_at=datetime.datetime(2020, 12, 1, tzinfo=datetime.timezone.utc),
            end_at=datetime.datetime(2020, 12, 3, tzinfo=datetime.timezone.utc),
        )
        assert {
            u1: TotalAmounts(
                steps=12, active_minutes=23, distance_km=decimal.Decimal("3.4")
            ),
            u2: TotalAmounts(
                steps=24, active_minutes=35, distance_km=decimal.Decimal("4.6")
            ),
        } == c.total_amounts()

    def test_weekend_warrior_seal_at(self):
        end_dt = datetime.datetime(year=2023, month=12, day=1)
        c = Challenge(challenge_type=ChallengeType.WEEKEND_WARRIOR.value, end_at=end_dt)
        assert (end_dt + datetime.timedelta(hours=24)) == c.seal_at

    def test_workweek_hustle_seal_at(self):
        end_dt = datetime.datetime(year=2023, month=12, day=1)
        c = Challenge(challenge_type=ChallengeType.WORKWEEK_HUSTLE.value, end_at=end_dt)
        assert (end_dt + datetime.timedelta(hours=24)) == c.seal_at

    def test_bingo_seal_at(self):
        end_dt = datetime.datetime(year=2023, month=12, day=1)
        c = Challenge(challenge_type=ChallengeType.BINGO.value, end_at=end_dt)
        assert end_dt == c.seal_at


def test_apply_fuzz_factor_to_int_minimum():
    assert 80 == apply_fuzz_factor_to_int(100, 20, -20)


def test_apply_fuzz_factor_to_int_midpoint():
    assert 100 == apply_fuzz_factor_to_int(100, 20, 0)


def test_apply_fuzz_factor_to_int_maximum():
    assert 120 == apply_fuzz_factor_to_int(100, 20, 20)


def test_apply_fuzz_factor_to_decimal_minimum():
    assert decimal.Decimal("0.8") == apply_fuzz_factor_to_decimal(
        decimal.Decimal("1.0"), 20, -20
    )


def test_apply_fuzz_factor_to_decimal_midpodecimal():
    assert decimal.Decimal("1.0") == apply_fuzz_factor_to_decimal(
        decimal.Decimal("1.0"), 20, 0
    )


def test_apply_fuzz_factor_to_decimal_maximum():
    assert decimal.Decimal("1.2") == apply_fuzz_factor_to_decimal(
        decimal.Decimal("1.0"), 20, 20
    )


class TestBingoTile:
    def test_flip_unflipped_tile(self, monkeypatch):
        curr_time = datetime.datetime.now(tz=datetime.timezone.utc)
        monkeypatch.setattr(
            datetime,
            "datetime",
            create_mock_datetime(curr_time),
        )

        t = BingoTile(flipped=False)
        t.flip()
        assert t.flipped
        assert curr_time == t.flipped_at

    def test_flip_flipped_tile(self):
        curr_time = datetime.datetime.now(tz=datetime.timezone.utc)
        t = BingoTile(flipped=True, flipped_at=curr_time)
        t.flip()
        assert t.flipped
        assert curr_time == t.flipped_at


class SampleBingoCardPattern(BingoCardPattern):
    @property
    def pattern(self) -> list[list[int]]:
        return [
            [1, 0, 1],
            [0, 1, 0],
            [1, 0, 1],
        ]


class TestBingoCard:
    def test_victory_tiles_returns_empty_when_no_tiles(self):
        c = BingoCard(bingo_tiles=[])
        assert 0 == len(list(c.victory_tiles()))

    def test_victory_tiles_returns_empty_when_all_tiles_not_required(self):
        t = BingoTile(required_for_win=False)
        c = BingoCard(bingo_tiles=[t])
        assert 0 == len(list(c.victory_tiles()))

    def test_victory_tiles_returns_tile_when_required(self):
        t1 = BingoTile(required_for_win=False)
        t2 = BingoTile(required_for_win=True)
        c = BingoCard(bingo_tiles=[t2, t1])
        victory_tiles = list(c.victory_tiles())
        assert 1 == len(victory_tiles)
        assert t2 in victory_tiles
        assert t1 not in victory_tiles

    def test_flipped_victory_tiles_returns_empty_when_no_tiles(self):
        c = BingoCard(bingo_tiles=[])
        assert 0 == len(list(c.flipped_victory_tiles()))

    def test_flipped_victory_tiles_returns_empty_when_all_tiles_not_required(self):
        t = BingoTile(flipped=True, required_for_win=False)
        c = BingoCard(bingo_tiles=[t])
        assert 0 == len(list(c.flipped_victory_tiles()))

    def test_flipped_victory_tiles_returns_empty_when_all_tiles_not_flipped(self):
        t = BingoTile(flipped=False, required_for_win=True)
        c = BingoCard(bingo_tiles=[t])
        assert 0 == len(list(c.flipped_victory_tiles()))

    def test_flipped_victory_tiles_returns_tile_when_required(self):
        t1 = BingoTile(flipped=True, required_for_win=False)
        t2 = BingoTile(flipped=True, required_for_win=True)
        c = BingoCard(bingo_tiles=[t2, t1])
        victory_tiles = list(c.flipped_victory_tiles())
        assert 1 == len(victory_tiles)
        assert t2 in victory_tiles
        assert t1 not in victory_tiles

    def test_flipped_victory_tiles_returns_tile_when_flipped(self):
        t1 = BingoTile(flipped=False, required_for_win=True)
        t2 = BingoTile(flipped=True, required_for_win=True)
        c = BingoCard(bingo_tiles=[t2, t1])
        victory_tiles = list(c.flipped_victory_tiles())
        assert 1 == len(victory_tiles)
        assert t2 in victory_tiles
        assert t1 not in victory_tiles

    def test_unflipped_victory_tiles_returns_empty_when_no_tiles(self):
        c = BingoCard(bingo_tiles=[])
        assert 0 == len(list(c.unflipped_victory_tiles()))

    def test_unflipped_victory_tiles_returns_empty_when_all_tiles_flipped(self):
        t = BingoTile(flipped=True, required_for_win=True)
        c = BingoCard(bingo_tiles=[t])
        assert 0 == len(list(c.unflipped_victory_tiles()))

    def test_unflipped_victory_tiles_returns_tile_when_required(self):
        t1 = BingoTile(flipped=True, required_for_win=False)
        t2 = BingoTile(flipped=False, required_for_win=True)
        c = BingoCard(bingo_tiles=[t2, t1])
        victory_tiles = list(c.unflipped_victory_tiles())
        assert 1 == len(victory_tiles)
        assert t2 in victory_tiles
        assert t1 not in victory_tiles

    def test_unfinished_returns_false_when_no_tiles(self):
        c = BingoCard(bingo_tiles=[])
        assert not c.unfinished()

    def test_unfinished_returns_false_when_all_tiles_flipped(self):
        t = BingoTile(flipped=True, required_for_win=False)
        c = BingoCard(bingo_tiles=[t])
        assert not c.unfinished()

        t = BingoTile(flipped=True, required_for_win=True)
        c = BingoCard(bingo_tiles=[t])
        assert not c.unfinished()

    def test_unfinished_returns_true_when_tile_unflipped(self):
        t = BingoTile(flipped=False, required_for_win=True)
        c = BingoCard(bingo_tiles=[t])
        assert c.unfinished()

    def test_finished_returns_true_when_no_tiles(self):
        c = BingoCard(bingo_tiles=[])
        assert c.finished()

    def test_finished_returns_true_when_all_tiles_flipped(self):
        t = BingoTile(flipped=True, required_for_win=False)
        c = BingoCard(bingo_tiles=[t])
        assert c.finished()

        t = BingoTile(flipped=True, required_for_win=True)
        c = BingoCard(bingo_tiles=[t])
        assert c.finished()

    def test_finished_returns_false_when_tile_unflipped(self):
        t = BingoTile(flipped=False, required_for_win=True)
        c = BingoCard(bingo_tiles=[t])
        assert not c.finished()

    def test_finished_at_returns_none_when_no_tiles(self):
        c = BingoCard(bingo_tiles=[])
        assert c.finished_at() is None

    def test_finished_at_returns_none_when_no_victory_tiles(self):
        t = BingoTile(flipped=True, required_for_win=False)
        c = BingoCard(bingo_tiles=[t])
        assert c.finished_at() is None

    def test_finished_at_returns_latest_timestamp_when_all_tiles_flipped(self):
        dt = datetime.datetime(
            year=2012,
            month=10,
            day=3,
            hour=11,
            minute=28,
            second=11,
            tzinfo=datetime.timezone.utc,
        )
        t = BingoTile(flipped=True, required_for_win=True, flipped_at=dt)
        c = BingoCard(bingo_tiles=[t])
        assert dt == c.finished_at() == dt

        dt1 = datetime.datetime(
            year=2012,
            month=10,
            day=3,
            hour=11,
            minute=28,
            second=11,
            tzinfo=datetime.timezone.utc,
        )
        t1 = BingoTile(flipped=True, required_for_win=True, flipped_at=dt1)
        dt2 = datetime.datetime(
            year=2013,
            month=10,
            day=3,
            hour=11,
            minute=28,
            second=11,
            tzinfo=datetime.timezone.utc,
        )
        t2 = BingoTile(flipped=True, required_for_win=True, flipped_at=dt2)
        c = BingoCard(bingo_tiles=[t1, t2])
        assert dt2 == c.finished_at()

    def test_finished_at_returns_none_when_tile_unflipped(self):
        t = BingoTile(flipped=False, required_for_win=True)
        c = BingoCard(bingo_tiles=[t])
        assert c.finished_at() is None

    def test_compute_total_amounts_for_resource_assigns_proportional_to_victory_tile_count(
        self, monkeypatch
    ):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        u = User()
        last_activity_dt = now - datetime.timedelta(hours=1)
        last_activity = UserActivity(
            created_at=last_activity_dt,
            steps=42,
            active_minutes=36,
            distance_km=decimal.Decimal(1.8),
        )
        monkeypatch.setattr(u, "last_activity", lambda: last_activity)

        def mock_latest_activity_for_days_within_timespan(
            start: datetime.datetime, end: datetime.datetime
        ) -> Generator[UserActivity, None, None]:
            yield last_activity

        monkeypatch.setattr(
            u,
            "latest_activity_for_days_within_timespan",
            mock_latest_activity_for_days_within_timespan,
        )

        card = BingoCard()
        start = now - datetime.timedelta(days=2)
        pattern = SampleBingoCardPattern()
        totals = card.compute_total_amounts_for_resource(u, start, now, pattern)

        # 42/30 * 2 / (5/9) = 5
        assert 5 == totals.steps

        # 36/30 * 2 / (5/9) = 4
        assert 4 == totals.active_minutes

        # 1.8/30 * 2 / (5/9) = 0.22
        assert decimal.Decimal("0.22") == totals.distance_km

    def test_compute_total_amounts_for_resource_calculates_average_over_past_month(
        self, monkeypatch
    ):
        now = datetime.datetime(
            year=2020, month=12, day=10, tzinfo=datetime.timezone.utc
        )
        # Average steps over the past 30d are 10000+20000+30000 = 60000, or 2k/day
        # minutes are 1000+2000+3000 = 6000, or 200/day
        # distance is 11.1+22.2+33.3 = 66.6, or 2.22/day
        # Average
        u = User(
            activities=[
                UserActivity(
                    created_at=now - datetime.timedelta(days=10),
                    record_date=(now - datetime.timedelta(days=10)).date(),
                    steps=10000,
                    active_minutes=1000,
                    distance_km=decimal.Decimal(11.1),
                ),
                UserActivity(
                    created_at=now - datetime.timedelta(days=20),
                    record_date=(now - datetime.timedelta(days=20)).date(),
                    steps=20000,
                    active_minutes=2000,
                    distance_km=decimal.Decimal(22.2),
                ),
                UserActivity(
                    created_at=now - datetime.timedelta(days=30),
                    record_date=(now - datetime.timedelta(days=30)).date(),
                    steps=30000,
                    active_minutes=3000,
                    distance_km=decimal.Decimal(33.3),
                ),
                UserActivity(
                    created_at=now - datetime.timedelta(days=40),
                    record_date=(now - datetime.timedelta(days=40)).date(),
                    steps=40000,
                    active_minutes=4000,
                    distance_km=decimal.Decimal(44.4),
                ),
            ]
        )

        card = BingoCard()
        # Set up a challenge over two days
        start = now - datetime.timedelta(days=2)
        pattern = SampleBingoCardPattern()
        totals = card.compute_total_amounts_for_resource(u, start, now, pattern)

        # (2k*2) / (5/9)
        assert 7200 == totals.steps

        # (200*2) / (5/9)
        assert 720 == totals.active_minutes

        # (2.22*2) / (5/9)
        assert decimal.Decimal("7.99") == totals.distance_km

    def test_create_for_user_and_challenge_creates_bonus_tiles(self):
        # 5x5 card, 25 tiles
        card = BingoCard()
        start = datetime.datetime(2022, 1, 1)
        end = datetime.datetime(2022, 1, 4)

        user = User(
            activities=[
                UserActivity(
                    created_at=datetime.datetime(2021, 12, 31),
                    record_date=datetime.date(2021, 12, 31),
                    steps=100,
                    active_minutes=42,
                    distance_km=decimal.Decimal("3.6"),
                ),
                UserActivity(
                    created_at=datetime.datetime(2021, 12, 30),
                    record_date=datetime.date(2021, 12, 30),
                    steps=100,
                    active_minutes=42,
                    distance_km=decimal.Decimal("3.6"),
                ),
            ]
        )
        challenge = Challenge()

        # 17 victory tiles
        pattern = BingoCard.PATTERNS[0]
        card.create_for_user_and_challenge(user, challenge, start, end, pattern)

        # 25 - 17 = 8 potential bonus tiles,
        # we fill half (4) of them.
        assert 4 == len([t for t in card.bingo_tiles if t.bonus_type is not None])

        # No victory tiles have bonuses.
        assert not any(t.bonus_type is not None for t in card.victory_tiles())

        # No bonus tiles give bonuses of the same type.
        assert not any(
            t.steps is not None
            and t.bonus_type == BingoTileBonusType.STEPS
            or t.active_minutes is not None
            and t.bonus_type == BingoTileBonusType.ACTIVE_MINUTES
            or t.distance_km is not None
            and t.bonus_type == BingoTileBonusType.DISTANCE_KM
            for t in card.bingo_tiles
        )

        # Total steps bonuses are within 20% of 1/10 the total activity.
        actual_step_bonuses = sum(
            t.bonus_amount if t.bonus_amount is not None else 0
            for t in card.bingo_tiles
            if t.bonus_type == BingoTileBonusType.STEPS
        )
        assert 20 >= actual_step_bonuses >= 0
        actual_minute_bonuses = sum(
            t.bonus_amount if t.bonus_amount is not None else 0
            for t in card.bingo_tiles
            if t.bonus_type == BingoTileBonusType.ACTIVE_MINUTES
        )
        assert 8 >= actual_minute_bonuses >= 0
        actual_distance_bonuses = sum(
            t.bonus_amount if t.bonus_amount is not None else 0
            for t in card.bingo_tiles
            if t.bonus_type == BingoTileBonusType.DISTANCE_KM
        )
        assert decimal.Decimal("0.72") >= actual_distance_bonuses >= 0

    def test_unused_amounts_with_no_activities_returns_zero(self):
        user = User(activities=[])
        challenge = Challenge(challenge_type=ChallengeType.BINGO.value)
        card = BingoCard(user=user, challenge=challenge)
        amounts = card.unused_amounts()
        assert 0 == amounts.steps
        assert 0 == amounts.activeMinutes
        assert decimal.Decimal(0) == amounts.distanceKm

    def test_unused_amounts_with_one_activity_returns_amount(self):
        user = User(
            activities=[
                UserActivity(
                    created_at=datetime.datetime(
                        2021, 12, 31, tzinfo=datetime.timezone.utc
                    ),
                    record_date=datetime.date(2021, 12, 31),
                    steps=100,
                    active_minutes=42,
                    distance_km=decimal.Decimal("3.6"),
                ),
            ]
        )
        challenge = Challenge(
            challenge_type=ChallengeType.BINGO.value,
            start_at=datetime.datetime(2021, 12, 30, tzinfo=datetime.timezone.utc),
            end_at=datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc),
        )
        card = BingoCard(user=user, challenge=challenge)
        amounts = card.unused_amounts()
        assert 100 == amounts.steps
        assert 42 == amounts.activeMinutes
        assert decimal.Decimal("3.6") == amounts.distanceKm

    def test_unused_amounts_with_unflipped_tile_does_not_count_amount(self):
        user = User(
            activities=[
                UserActivity(
                    created_at=datetime.datetime(
                        2021, 12, 31, tzinfo=datetime.timezone.utc
                    ),
                    record_date=datetime.date(2021, 12, 31),
                    steps=100,
                    active_minutes=42,
                    distance_km=decimal.Decimal("3.6"),
                ),
            ]
        )
        challenge = Challenge(
            challenge_type=ChallengeType.BINGO.value,
            start_at=datetime.datetime(2021, 12, 30, tzinfo=datetime.timezone.utc),
            end_at=datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc),
        )
        card = BingoCard(
            user=user,
            challenge=challenge,
            bingo_tiles=[
                BingoTile(
                    steps=23,
                    flipped=False,
                )
            ],
        )
        amounts = card.unused_amounts()
        assert 100 == amounts.steps
        assert 42 == amounts.activeMinutes
        assert decimal.Decimal("3.6") == amounts.distanceKm

    def test_unused_amounts_with_flipped_tile_returns_reduced_amount(self):
        user = User(
            activities=[
                UserActivity(
                    created_at=datetime.datetime(
                        2021, 12, 31, tzinfo=datetime.timezone.utc
                    ),
                    record_date=datetime.date(2021, 12, 31),
                    steps=100,
                    active_minutes=42,
                    distance_km=decimal.Decimal("3.6"),
                ),
            ]
        )
        challenge = Challenge(
            challenge_type=ChallengeType.BINGO.value,
            start_at=datetime.datetime(2021, 12, 30, tzinfo=datetime.timezone.utc),
            end_at=datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc),
        )
        card = BingoCard(
            user=user,
            challenge=challenge,
            bingo_tiles=[
                BingoTile(flipped=True, steps=11),
                BingoTile(
                    flipped=True,
                    active_minutes=3,
                ),
                BingoTile(
                    flipped=True,
                    distance_km=decimal.Decimal("1.1"),
                ),
            ],
        )
        amounts = card.unused_amounts()
        # 100 - 11
        assert 89 == amounts.steps
        # 42 - 3
        assert 39 == amounts.activeMinutes
        # 3.6 - 1.1
        assert decimal.Decimal("2.5") == amounts.distanceKm

    def test_unused_amounts_with_unflipped_bonus_tile_does_not_count(self):
        user = User(
            activities=[
                UserActivity(
                    created_at=datetime.datetime(
                        2021, 12, 31, tzinfo=datetime.timezone.utc
                    ),
                    record_date=datetime.date(2021, 12, 31),
                    steps=100,
                    active_minutes=42,
                    distance_km=decimal.Decimal("3.6"),
                ),
            ]
        )
        challenge = Challenge(
            challenge_type=ChallengeType.BINGO.value,
            start_at=datetime.datetime(2021, 12, 30, tzinfo=datetime.timezone.utc),
            end_at=datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc),
        )
        card = BingoCard(
            user=user,
            challenge=challenge,
            bingo_tiles=[
                BingoTile(flipped=True, steps=11),
                BingoTile(
                    flipped=False,
                    bonus_type=BingoTileBonusType.STEPS.value,
                    bonus_amount=10,
                ),
            ],
        )
        amounts = card.unused_amounts()
        # 100 - 11
        assert 89 == amounts.steps

    def test_unused_amounts_with_flipped_bonus_tile_counts(self):
        user = User(
            activities=[
                UserActivity(
                    created_at=datetime.datetime(
                        2021, 12, 31, tzinfo=datetime.timezone.utc
                    ),
                    record_date=datetime.date(2021, 12, 31),
                    steps=100,
                    active_minutes=42,
                    distance_km=decimal.Decimal("3.6"),
                ),
            ]
        )
        challenge = Challenge(
            challenge_type=ChallengeType.BINGO.value,
            start_at=datetime.datetime(2021, 12, 30, tzinfo=datetime.timezone.utc),
            end_at=datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc),
        )
        card = BingoCard(
            user=user,
            challenge=challenge,
            bingo_tiles=[
                BingoTile(flipped=True, steps=11),
                BingoTile(
                    flipped=True,
                    bonus_type=BingoTileBonusType.STEPS.value,
                    bonus_amount=10,
                ),
                BingoTile(flipped=True, active_minutes=3),
                BingoTile(
                    flipped=True,
                    bonus_type=BingoTileBonusType.ACTIVE_MINUTES.value,
                    bonus_amount=6,
                ),
                BingoTile(flipped=True, distance_km=decimal.Decimal("1.1")),
                BingoTile(
                    flipped=True,
                    bonus_type=BingoTileBonusType.DISTANCE_KM.value,
                    bonus_amount=234,
                ),
            ],
        )
        amounts = card.unused_amounts()
        # 100 + 10 - 11
        assert 99 == amounts.steps

        # 42 + 6 - 3
        assert 45 == amounts.activeMinutes

        # 3.6 + 2.34 - 1.1
        assert decimal.Decimal("4.84") == amounts.distanceKm


class TestUser:
    def test_latest_activity_for_days_within_timespan_with_no_activities_returns_empty(
        self,
    ):
        u = User(activities=[])
        end = datetime.datetime(
            year=2020, month=12, day=10, tzinfo=datetime.timezone.utc
        )
        start = end - datetime.timedelta(hours=1)
        assert [] == list(
            u.latest_activity_for_days_within_timespan(start=start, end=end)
        )

    def test_latest_activity_for_days_within_timespan_filters_out_activities_before_start(
        self,
    ):
        start = datetime.datetime(
            year=2020, month=12, day=9, tzinfo=datetime.timezone.utc
        )
        end = datetime.datetime(
            year=2020, month=12, day=10, tzinfo=datetime.timezone.utc
        )
        activities = [
            UserActivity(
                record_date=datetime.date(year=2020, month=10, day=10),
                created_at=datetime.datetime(
                    year=2020, month=10, day=10, tzinfo=datetime.timezone.utc
                ),
            ),
            UserActivity(
                record_date=datetime.date(year=2020, month=12, day=9),
                created_at=datetime.datetime(
                    year=2020, month=12, day=9, hour=1, tzinfo=datetime.timezone.utc
                ),
            ),
        ]
        u = User(activities=activities)

        assert [activities[1]] == list(
            u.latest_activity_for_days_within_timespan(start=start, end=end)
        )

    def test_latest_activity_for_days_within_timespan_filters_out_activities_after_end(
        self,
    ):
        start = datetime.datetime(
            year=2020, month=10, day=9, tzinfo=datetime.timezone.utc
        )
        end = datetime.datetime(
            year=2020, month=10, day=10, hour=2, tzinfo=datetime.timezone.utc
        )
        activities = [
            UserActivity(
                record_date=datetime.date(year=2020, month=10, day=10),
                created_at=datetime.datetime(
                    year=2020, month=10, day=10, tzinfo=datetime.timezone.utc
                ),
            ),
            UserActivity(
                record_date=datetime.date(year=2020, month=12, day=9),
                created_at=datetime.datetime(
                    year=2020, month=12, day=9, hour=1, tzinfo=datetime.timezone.utc
                ),
            ),
        ]
        u = User(activities=activities)

        assert [activities[0]] == list(
            u.latest_activity_for_days_within_timespan(start=start, end=end)
        )

    def test_latest_activity_for_days_within_timespan_filters_out_prior_activities_for_day(
        self,
    ):
        start = datetime.datetime(
            year=2020, month=10, day=9, tzinfo=datetime.timezone.utc
        )
        end = datetime.datetime(
            year=2020, month=10, day=11, hour=2, tzinfo=datetime.timezone.utc
        )
        activities = [
            UserActivity(
                record_date=datetime.date(year=2020, month=10, day=10),
                created_at=datetime.datetime(
                    year=2020, month=10, day=10, tzinfo=datetime.timezone.utc
                ),
            ),
            UserActivity(
                record_date=datetime.date(year=2020, month=10, day=10),
                created_at=datetime.datetime(
                    year=2020, month=10, day=10, hour=1, tzinfo=datetime.timezone.utc
                ),
            ),
            UserActivity(
                record_date=datetime.date(year=2020, month=10, day=11),
                created_at=datetime.datetime(
                    year=2020, month=10, day=11, hour=1, tzinfo=datetime.timezone.utc
                ),
            ),
        ]
        u = User(activities=activities)

        assert [
            activities[1],
            activities[2],
        ] == list(u.latest_activity_for_days_within_timespan(start=start, end=end))
