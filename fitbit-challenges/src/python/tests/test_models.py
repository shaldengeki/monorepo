import datetime
import pytest

from ..config import app, db
from ..models import Challenge, User


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
