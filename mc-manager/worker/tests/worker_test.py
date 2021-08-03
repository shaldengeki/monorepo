import pytest
import requests

from worker.worker import fetch_expected_servers, split_s3_path


class MockResponse:
    def __init__(self, response):
        self.response = response

    def json(self):
        return self.response


def test_split_s3_path():
    assert split_s3_path("s3://my-bucket/some/path/to/key") == (
        "my-bucket",
        "some/path/to/key",
    )


def test_fetch_expected_servers(monkeypatch):
    def mock_post(*args, **kwargs):
        return MockResponse({"data": {"servers": [{"id": 1, "name": "test-server"}]}})

    monkeypatch.setattr(requests, "post", mock_post)

    expected = [{"id": 1, "name": "test-server"}]
    actual = fetch_expected_servers("fake-host", 0)
    assert actual == expected


def test_fetch_expected_servers_empty(monkeypatch):
    def mock_post(*args, **kwargs):
        return MockResponse({})

    monkeypatch.setattr(requests, "post", mock_post)

    expected = []
    actual = fetch_expected_servers("fake-host", 0)
    assert actual == expected


def test_fetch_expected_servers_error(monkeypatch):
    def mock_post(*args, **kwargs):
        return MockResponse({"error": "test failure"})

    monkeypatch.setattr(requests, "post", mock_post)

    with pytest.raises(ValueError):
        fetch_expected_servers("fake-host", 0)


if __name__ == "__main__":
    raise SystemExit(pytest.main())
