import pytest
from worker.worker import split_s3_path


def test_split_s3_path():
    assert split_s3_path("s3://my-bucket/some/path/to/key") == (
        "my-bucket",
        "some/path/to/key",
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main())
