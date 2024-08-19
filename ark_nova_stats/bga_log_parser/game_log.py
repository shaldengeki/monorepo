from dataclasses import dataclass
from typing import Any, Iterator, Optional

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

    def parse_player_stats(self, stats: dict[str, Any]) -> PlayerStats:
        return PlayerStats(
            player_id=int(stats["player"]),
            score=int(stats["score"]),
            rank=int(stats["rank"]),
            thinking_time=int(stats["stats"]["1"]),
            starting_position=int(stats["stats"]["11"]),
            turns=int(stats["stats"]["12"]),
            breaks_triggered=int(stats["stats"]["13"]),
            triggered_end=bool(int(stats["stats"]["14"])),
            map_id=int(stats["stats"]["15"]),
            appeal=int(stats["stats"]["16"]),
            conservation=int(stats["stats"]["17"]),
            reputation=int(stats["stats"]["19"]),
            actions_build=int(stats["stats"]["20"]),
            actions_animals=int(stats["stats"]["21"]),
            actions_cards=int(stats["stats"]["22"]),
            actions_association=int(stats["stats"]["23"]),
            actions_sponsors=int(stats["stats"]["24"]),
            x_tokens_gained=int(stats["stats"]["25"]),
            x_actions=int(stats["stats"]["26"]),
            x_tokens_used=int(stats["stats"]["27"]),
            money_gained=int(stats["stats"]["30"]),
            money_gained_through_income=int(stats["stats"]["31"]),
            money_spent_on_animals=int(stats["stats"]["32"]),
            money_spent_on_enclosures=int(stats["stats"]["33"]),
            money_spent_on_donations=int(stats["stats"]["34"]),
            money_spent_on_playing_cards_from_reputation_range=int(
                stats["stats"]["35"]
            ),
            cards_drawn_from_deck=int(stats["stats"]["40"]),
            cards_drawn_from_reputation_range=int(stats["stats"]["41"]),
            cards_snapped=int(stats["stats"]["42"]),
            cards_discarded=int(stats["stats"]["43"]),
            played_sponsors=int(stats["stats"]["44"]),
            played_animals=int(stats["stats"]["45"]),
            release_animals=int(stats["stats"]["46"]),
            association_workers=int(stats["stats"]["50"]),
            association_donations=int(stats["stats"]["51"]),
            association_reputation_actions=int(stats["stats"]["52"]),
            association_partner_zoo_actions=int(stats["stats"]["53"]),
            association_university_actions=int(stats["stats"]["54"]),
            association_conservation_project_actions=int(stats["stats"]["55"]),
            built_enclosures=int(stats["stats"]["60"]),
            built_kiosks=int(stats["stats"]["61"]),
            built_pavilions=int(stats["stats"]["62"]),
            built_unique_buildings=int(stats["stats"]["63"]),
            hexes_covered=int(stats["stats"]["64"]),
            hexes_empty=int(stats["stats"]["65"]),
            upgraded_action_cards=int(stats["stats"]["70"]),
            upgraded_animals=bool(int(stats["stats"]["71"])),
            upgraded_build=bool(int(stats["stats"]["72"])),
            upgraded_cards=bool(int(stats["stats"]["73"])),
            upgraded_sponsors=bool(int(stats["stats"]["74"])),
            upgraded_association=bool(int(stats["stats"]["75"])),
            icons_africa=int(stats["stats"]["76"]),
            icons_europe=int(stats["stats"]["77"]),
            icons_asia=int(stats["stats"]["78"]),
            icons_australia=int(stats["stats"]["79"]),
            icons_americas=int(stats["stats"]["80"]),
            icons_bird=int(stats["stats"]["81"]),
            icons_predator=int(stats["stats"]["82"]),
            icons_herbivore=int(stats["stats"]["83"]),
            icons_bear=int(stats["stats"]["84"]),
            icons_reptile=int(stats["stats"]["85"]),
            icons_primate=int(stats["stats"]["86"]),
            icons_petting_zoo=int(stats["stats"]["97"]),
            icons_sea_animal=int(stats["stats"]["91"]),
            icons_water=int(stats["stats"]["88"]),
            icons_rock=int(stats["stats"]["89"]),
            icons_science=int(stats["stats"]["90"]),
        )

    def parse_game_stats(self) -> Stats:
        # Player stats are in last event.
        if not self.data.logs:
            raise StatsNotSetError()

        # The stats are in a log that's close to the end.
        # It doesn't get deterministically emitted in any given position,
        # so we search for it.
        stats = None
        for l in self.data.logs[-10:]:
            if any(
                e.args
                and "args" in e.args
                and e.args["args"]
                and "result" in e.args["args"]
                for e in l.data
            ):
                stats = next(
                    e.args["args"]["result"]
                    for e in l.data
                    if e.args
                    and "args" in e.args
                    and e.args["args"]
                    and "result" in e.args["args"]
                )
                break

        if stats is None:
            print(self.data.logs[-10:])
            raise StatsNotSetError()

        return Stats(
            player_stats=[
                self.parse_player_stats(player_stats) for player_stats in stats
            ]
        )
