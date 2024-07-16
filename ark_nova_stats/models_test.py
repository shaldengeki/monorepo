import datetime
import decimal
import pytest
import sys
from typing import Generator

from ark_nova_stats.models import ExampleModel


class TestExampleModel:
    def test_sample(self):
        assert ExampleModel(id=1)

if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))