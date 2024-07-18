import datetime
import decimal
import sys
from typing import Generator

import pytest

from ark_nova_stats.models import GameLog


class TestGameLog:
    def test_sample(self):
        assert GameLog(id=1)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
