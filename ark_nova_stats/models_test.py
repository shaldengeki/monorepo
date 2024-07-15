import datetime
import decimal
from typing import Generator

from ark_nova_stats.models import ExampleModel


class TestExampleModel:
    def test_sample(self):
        assert ExampleModel(id=1)
