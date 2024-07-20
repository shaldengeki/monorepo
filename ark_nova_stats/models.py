import dataclasses
import datetime
import decimal
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


class GameLog(db.Model):
    __tablename__ = "game_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    log: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )
