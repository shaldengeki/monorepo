import dataclasses
import datetime
import decimal
import enum
import itertools
import random
from typing import TYPE_CHECKING, Generator, Optional

import requests
from sqlalchemy import ForeignKey, desc
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.functions import now

from skeleton.config import db

# SQLAlchemy defines the db.Model type dynamically, which doesn't work with mypy.
# We therefore import it explicitly in the typechecker, so this resolves.
if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model
else:
    Model = db.Model


class ExampleModel(Model):
    __tablename__ = "example_models"

    id: Mapped[int] = mapped_column(primary_key=True)
