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

from ark_nova_stats.config import db


class ExampleModel(db.Model):
    __tablename__ = "example_models"

    id: Mapped[int] = mapped_column(primary_key=True)
