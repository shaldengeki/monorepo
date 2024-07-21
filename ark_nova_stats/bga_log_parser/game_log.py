from dataclasses import dataclass
from typing import Optional


@dataclass
class GameLogEventData:
    uid: str
    type: str
    log: str
    args: dict
    lock_uuid: Optional[str] = None
    synchro: Optional[int] = None
    h: Optional[str] = None

    PLAY_LOGS = [
        "plays",
        "supports a conservation project",
        "and places it in",
        "buys",
    ]

    @property
    def is_play_action(self) -> bool:
        if "card_name" not in self.args:
            return False

        return any(play_log in self.log for play_log in self.PLAY_LOGS)


@dataclass
class GameLogEvent:
    channel: str
    table_id: int
    packet_id: str
    packet_type: str
    time: int
    data: list[GameLogEventData]
    move_id: Optional[int] = None

    def __post_init__(self):
        self.table_id = int(self.table_id)
        if self.move_id is not None:
            self.move_id = int(self.move_id)
        self.time = int(self.time)
        self.data = [GameLogEventData(**x) for x in self.data]  # type: ignore


@dataclass
class GameLogPlayer:
    id: int
    color: str
    name: str
    avatar: str


@dataclass
class GameLogData:
    logs: list[GameLogEvent]
    players: list[GameLogPlayer]

    def __post_init__(self):
        self.players = [GameLogPlayer(**x) for x in self.players]  # type: ignore
        self.logs = [GameLogEvent(**x) for x in self.logs]  # type: ignore


@dataclass
class GameLog:
    status: int
    data: GameLogData

    def __post_init__(self):
        self.data = GameLogData(**self.data)  # type: ignore

    @property
    def winner(self) -> Optional[GameLogPlayer]:
        if not self.data.logs:
            return None

        # Look at the last move.
        last_move = self.data.logs[-1]
        victory_event = next(
            e for e in last_move.data if e.type == "simpleNode" and "wins!" in e.log
        )
        return next(
            p for p in self.data.players if p.name == victory_event.args["player_name"]
        )
