from dataclasses import dataclass
from typing import Optional


@dataclass
class GameLogEntryData:
    uid: str
    type: str
    log: str
    args: dict
    lock_uuid: Optional[str] = None
    synchro: Optional[int] = None
    h: Optional[str] = None


@dataclass
class GameLogEntry:
    channel: str
    table_id: str
    packet_id: str
    packet_type: str
    move_id: str
    time: str
    data: list[GameLogEntryData]

    def __post_init__(self):
        self.data = [GameLogEntryData(**x) for x in self.data]  # type: ignore


@dataclass
class GameLogPlayer:
    id: int
    color: str
    name: str
    avatar: str


@dataclass
class GameLogData:
    logs: list[GameLogEntry]
    players: list[GameLogPlayer]

    def __post_init__(self):
        self.players = [GameLogPlayer(**x) for x in self.players]  # type: ignore
        self.logs = [GameLogEntry(**x) for x in self.logs]  # type: ignore


@dataclass
class GameLog:
    status: int
    data: GameLogData

    def __post_init__(self):
        self.data = GameLogData(**self.data)  # type: ignore
