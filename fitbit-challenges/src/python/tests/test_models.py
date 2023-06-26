import datetime
import decimal

from ..models import Challenge, apply_fuzz_factor_to_int, apply_fuzz_factor_to_decimal


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
