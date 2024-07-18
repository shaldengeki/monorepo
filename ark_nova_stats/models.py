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


@dataclasses.dataclass
class GameLogDataLogDataJSON:
    uid: str
    type: str
    log: str
    synchro: int
    args: dict


@dataclasses.dataclass
class GameLogDataLogJSON:
    channel: str
    table_id: str
    packet_id: str
    packet_type: str
    move_id: str
    time: str
    data: list[GameLogDataLogDataJSON]

    def __post_init__(self):
        self.data = [GameLogDataLogDataJSON(**x) for x in self.data]


@dataclasses.dataclass
class GameLogDataPlayerJSON:
    id: int
    color: str
    name: str
    avatar: str


@dataclasses.dataclass
class GameLogDataJSON:
    logs: list
    players: list[GameLogDataPlayerJSON]

    def __post_init__(self):
        self.players = [GameLogDataPlayerJSON(**x) for x in self.players]


@dataclasses.dataclass
class GameLogContainerJSON:
    status: int
    data: GameLogDataJSON

    def __post_init__(self):
        self.data = GameLogDataJSON(**self.data)


class GameLog(db.Model):
    __tablename__ = "game_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    log: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )
