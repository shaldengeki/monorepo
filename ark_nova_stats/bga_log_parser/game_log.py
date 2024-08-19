from dataclasses import dataclass
from typing import Iterator, Optional

from ark_nova_stats.bga_log_parser.exceptions import (
    MoveNotSetError,
    NonArkNovaReplayError,
    PlayerNotFoundError,
    StatsNotSetError,
)
from ark_nova_stats.bga_log_parser.proto.game_pb2 import Game
from ark_nova_stats.bga_log_parser.proto.stats_pb2 import PlayerStats, Stats


@dataclass
class GameLogEventDataCard:
    name: str
    id: str


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
        "plays a new conservation project",
        "and places it in",
        "buys",
    ]

    @property
    def is_play_action(self) -> bool:
        if "card_name" not in self.args and "cards" not in self.args:
            return False

        return any(play_log in self.log for play_log in self.PLAY_LOGS)

    @property
    def played_card_names(self) -> Optional[set[str]]:
        card_names = set()
        if "card_name" in self.args:
            card_names.add(self.args["card_name"])
        elif "card_names" in self.args:
            # potentially multiple cards are played in this action.
            for arg_key, arg_val in self.args["card_names"]["args"].items():
                if "args" in arg_val and "card_name" in arg_val["args"]:
                    card_names.add(arg_val["args"]["card_name"])
        else:
            return None

        return card_names

    @property
    def played_cards(self) -> Optional[list[GameLogEventDataCard]]:
        cards = []
        if "card_name" in self.args:
            cards = [
                GameLogEventDataCard(
                    name=self.args["card_name"], id=self.args["card_id"]
                )
            ]
        elif "card_names" in self.args:
            # potentially multiple cards are played in this action.
            for arg_key, arg_val in self.args["card_names"]["args"].items():
                if "args" in arg_val and "card_name" in arg_val["args"]:
                    cards.append(
                        GameLogEventDataCard(
                            name=arg_val["args"]["card_name"],
                            id=arg_val["args"]["card_id"],
                        )
                    )
        else:
            return None

        return cards

    @property
    def player(self) -> Optional[dict[str, int | str]]:
        player_data = {
            "id": self.args.get("player_id", None),
            "name": self.args.get("player_name", None),
        }

        if all(v is None for v in player_data.values()):
            return None

        return player_data


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
class GameLogCardPlay:
    card: GameLogEventDataCard
    player: GameLogPlayer
    move: int


@dataclass
class GameLogData:
    logs: list[GameLogEvent]
    players: list[GameLogPlayer]

    def __post_init__(self):
        self.players = [GameLogPlayer(**x) for x in self.players]  # type: ignore
        self.logs = [GameLogEvent(**x) for x in self.logs]  # type: ignore
        self.validate_is_ark_nova_game()

    def validate_is_ark_nova_game(self) -> None:
        """
        Raises an exception if the currently-loaded game log is not for an Ark Nova game.
        It turns out that the game log itself doesn't contain the game name or ID on BGA.
        So we have to lossily infer this from what's in the data.
        """

        # Check to see if there's a scoring card draw in the first few actions.
        if not any(
            "from the deck (scoring cards)" in data.log
            for log in self.logs[:20]
            for data in log.data
        ):
            raise NonArkNovaReplayError()

    @property
    def card_plays(self) -> Iterator[GameLogCardPlay]:
        for log in self.logs:
            for d in log.data:
                if not d.is_play_action or d.played_cards is None:
                    continue

                for c in d.played_cards:
                    if log.move_id is None:
                        raise MoveNotSetError()

                    if d.player is None:
                        raise PlayerNotFoundError()

                    find_player = [p for p in self.players if p.id == d.player["id"]]
                    if not find_player:
                        raise PlayerNotFoundError()

                    yield GameLogCardPlay(
                        card=c,
                        move=log.move_id,
                        player=find_player[0],
                    )


@dataclass
class GameLog:
    status: int
    data: GameLogData

    def __post_init__(self):
        self.data = GameLogData(**self.data)  # type: ignore
        # TODO: populate this from self.data.
        self.game = Game()
        self.stats = self.parse_game_stats()

    @property
    def table_id(self) -> Optional[int]:
        if not self.data.logs:
            return None

        return self.data.logs[0].table_id

    @property
    def winner(self) -> Optional[GameLogPlayer]:
        if not self.data.logs:
            return None

        # Look at the last move.
        last_move = self.data.logs[-1]
        try:
            victory_event = next(
                e for e in last_move.data if e.type == "simpleNode" and "wins!" in e.log
            )
        except StopIteration:
            # No winner.
            return None

        return next(
            p for p in self.data.players if p.name == victory_event.args["player_name"]
        )

    @property
    def is_tie(self) -> bool:
        if not self.data.logs:
            return False

        # Look at the last move.
        last_move = self.data.logs[-1]

        return any(
            e.type == "simpleNode" and "End of game (tie)" in e.log
            for e in last_move.data
        )

    def parse_player_stats(self) -> list[PlayerStats]:
        # Player stats are in last event.
        if not self.data.logs:
            raise StatsNotSetError()

        print(self.data.logs[-1])

        return []

    def parse_game_stats(self) -> Stats:
        return Stats(player_stats=self.parse_player_stats())
