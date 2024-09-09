import dataclasses
from collections import Counter, defaultdict
from typing import Optional

from ark_nova_stats.bga_log_parser.game_log import GameLog
from ark_nova_stats.emu_cup.player_elos import PlayerELOs


@dataclasses.dataclass
class CardELORecord:
    card_name: str
    games: int = 0
    total_points: float = 0.0

    def add_points(self, points: float):
        self.total_points += points
        self.games += 1

    @property
    def avg_points(self) -> Optional[float]:
        if self.games == 0:
            return None

        return self.total_points / self.games

    def bayesian_avg_points(
        self, global_points: float, global_games: float
    ) -> Optional[float]:
        if self.games == 0:
            return None

        return (self.total_points + global_points) * 1.0 / (self.games + global_games)


@dataclasses.dataclass
class CardWinRateELOAdjustedOutput:
    rank: int
    card: str
    rate: float
    plays: int
    rate_bayes: float


def probability_of_win(elo_1: int, elo_2: int) -> float:
    return 1.0 / (1 + pow(10, ((elo_2 - elo_1) / 400.0)))


class CardWinRateELOAdjusted:
    def __init__(self):
        self.all_cards: Counter[str] = Counter()
        self.game_card_records: dict[str, CardELORecord] = {}
        self.average_plays = None
        self.outputs = None
        self.player_cards: defaultdict[int, set[str]] = defaultdict(lambda: set())

    def process_game(self, log: GameLog, elos: dict[int, PlayerELOs]) -> None:
        if len(log.data.players) != 2:
            print(f"Skipping log, not a two-player game")

        winrates_by_id: dict[int, float] = {
            log.data.players[0].id: probability_of_win(
                elos[log.data.players[0].id].prior_elo,
                elos[log.data.players[1].id].prior_elo,
            ),
            log.data.players[1].id: probability_of_win(
                elos[log.data.players[1].id].prior_elo,
                elos[log.data.players[0].id].prior_elo,
            ),
        }

        game_cards = self.game_log_cards(log)

        winner = log.winner
        for player_id, player_cards in game_cards.items():
            self.all_cards.update(player_cards)
            self.player_cards[player_id] = self.player_cards[player_id].union(
                player_cards
            )

            for card in player_cards:
                if card not in self.game_card_records:
                    self.game_card_records[card] = CardELORecord(card_name=card)

                result: int | float
                if winner is not None and player_id == winner.id:
                    result = 1
                elif log.is_tie:
                    result = 0.5
                else:
                    result = 0
                self.game_card_records[card].add_points(
                    result - winrates_by_id[player_id]
                )

    def game_log_cards(self, log: GameLog) -> dict[int, set[str]]:
        game_cards: defaultdict[int, set[str]] = defaultdict(lambda: set())
        for event in log.data.logs:
            for event_data in event.data:
                if not event_data.is_play_action:
                    continue

                card_names = event_data.played_card_names
                if card_names is None:
                    continue

                if event_data.player is not None:
                    player_id: int = int(event_data.player["id"])
                    game_cards[player_id] = game_cards[player_id].union(card_names)

        return game_cards

    def output(self, card: str) -> CardWinRateELOAdjustedOutput:
        if self.average_plays is None:
            if len(self.game_card_records) > 0:
                self.average_plays = (
                    1.0
                    * sum(record.games for record in self.game_card_records.values())
                    / len(self.game_card_records)
                )
            else:
                self.average_plays = 0

        if self.outputs is None:
            self.outputs = {
                card: CardWinRateELOAdjustedOutput(
                    rank=rank + 1,
                    card=card,
                    rate=(
                        0
                        if record.avg_points is None
                        else round(record.avg_points * 100, 2)
                    ),
                    plays=record.games,
                    rate_bayes=round(record.bayesian_avg_points(0, self.average_plays) * 100, 2),  # type: ignore
                )
                for rank, (card, record) in enumerate(self.game_card_records.items())
            }

        return self.outputs[card]


class OpeningHandWinRateELOAdjusted(CardWinRateELOAdjusted):
    def game_log_cards(self, log: GameLog) -> dict[int, set[str]]:
        game_cards: defaultdict[int, set[str]] = defaultdict(lambda: set())
        for player_id, hand_cards in log.data.opening_hands.items():
            hand_card_names = [card.name for card in hand_cards]
            game_cards[player_id] = game_cards[player_id].union(hand_card_names)

        return game_cards
