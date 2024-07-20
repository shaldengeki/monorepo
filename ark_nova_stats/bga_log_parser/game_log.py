from dataclasses import dataclass


@dataclass
class GameLogDataLogDataJSON:
    uid: str
    type: str
    log: str
    synchro: int
    args: dict


@dataclass
class GameLogDataLogJSON:
    channel: str
    table_id: str
    packet_id: str
    packet_type: str
    move_id: str
    time: str
    data: list[GameLogDataLogDataJSON]

    def __post_init__(self):
        self.data = [GameLogDataLogDataJSON(**x) for x in self.data]  # type: ignore


@dataclass
class GameLogDataPlayerJSON:
    id: int
    color: str
    name: str
    avatar: str


@dataclass
class GameLogDataJSON:
    logs: list
    players: list[GameLogDataPlayerJSON]

    def __post_init__(self):
        self.players = [GameLogDataPlayerJSON(**x) for x in self.players]  # type: ignore


@dataclass
class GameLogContainerJSON:
    status: int
    data: GameLogDataJSON

    def __post_init__(self):
        self.data = GameLogDataJSON(**self.data)  # type: ignore
