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
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.sql import func
from sqlalchemy.sql.functions import now

from skeleton.config import db

class Base(DeclarativeBase):
    pass

class ExampleModel(Base):
    __tablename__ = "example_models"

    id: Mapped[int] = mapped_column(primary_key=True)
