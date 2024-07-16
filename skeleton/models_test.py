import datetime
import decimal
from typing import Generator

from skeleton.models import ExampleModel


class TestExampleModel:
    def test_sample(self):
        assert ExampleModel(id=1)
