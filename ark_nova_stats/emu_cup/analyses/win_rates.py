import dataclasses
from collections import Counter, defaultdict
from typing import Optional

from ark_nova_stats.bga_log_parser.game_log import GameLog


@dataclasses.dataclass
class CardRecord:
    card_name: str
    wins: int = 0
    losses: int = 0

    @property
    def win_rate(self) -> Optional[float]:
        if self.wins == 0 and self.losses == 0:
            return None

        return self.wins * 1.0 / (self.wins + self.losses)

    def bayesian_win_rate(
        self, global_wins: float, global_plays: float
    ) -> Optional[float]:
        if self.wins == 0 and self.losses == 0:
            return None

        return (
            (self.wins + global_wins) * 1.0 / (self.wins + self.losses + global_plays)
        )


@dataclasses.dataclass
class CardRawWinRateOutput:
    rank: int
    card: str
    rate: float
    plays: int
    rate_bayes: float


class CardRawWinRate:
    def __init__(self):
        self.all_cards: Counter[str] = Counter()
        self.winner_cards: Counter[str] = Counter()
        self.loser_cards: Counter[str] = Counter()
        self.game_card_records: dict[str, CardRecord] = {}
        self.global_stats = None
        self.outputs = None
        self.player_cards: defaultdict[int, set[str]] = defaultdict(lambda: set())

    def process_game(self, log: GameLog) -> None:
        winner = log.winner

        game_cards = self.game_log_cards(log)

        winner = log.winner
        for player_id, player_cards in game_cards.items():
            self.all_cards.update(player_cards)

            self.player_cards[player_id] = self.player_cards[player_id].union(
                player_cards
            )

            for card in player_cards:
                if card not in self.game_card_records:
                    self.game_card_records[card] = CardRecord(card_name=card)

                if winner is not None and player_id == winner.id:
                    self.game_card_records[card].wins += 1
                elif log.is_tie:
                    self.game_card_records[card].wins += 1
                    self.game_card_records[card].losses += 1
                else:
                    self.game_card_records[card].losses += 1

    def game_log_cards(self, log: GameLog) -> dict[int, set[str]]:
        game_cards: defaultdict[int, set[str]] = defaultdict(lambda: set())
        for event in log.data.logs:
            for event_data in event.data:
                if not event_data.is_play_action:
                    continue

                card_names = event_data.played_card_names
                if card_names is None:
                    continue

                if log.is_tie:
                    continue

                if event_data.player is not None:
                    if event_data.player["id"] is None:
                        raise ValueError(
                            f"Player ID not set for log event: {event_data}"
                        )
                    player_id: int = int(event_data.player["id"])
                    game_cards[player_id] = game_cards[player_id].union(card_names)

        return game_cards

    def output(self, card) -> CardRawWinRateOutput:
        if self.global_stats is None:
            global_stats = [
                (record.wins, record.wins + record.losses)
                for _, record in self.game_card_records.items()
            ]

            self.global_stats = {}
            self.global_stats["total_wins"] = sum(wins for wins, _ in global_stats)
            self.global_stats["average_wins"] = (
                self.global_stats["total_wins"] * 1.0 / (len(global_stats) or 1)
            )
            self.global_stats["total_plays"] = sum(plays for _, plays in global_stats)
            self.global_stats["average_plays"] = (
                self.global_stats["total_plays"] * 1.0 / (len(global_stats) or 1)
            )

        if self.outputs is None:
            self.outputs = {
                card: CardRawWinRateOutput(
                    rank=rank + 1,
                    card=card,
                    rate=(
                        0
                        if record.win_rate is None
                        else round(record.win_rate * 100, 2)
                    ),
                    plays=record.wins + record.losses,
                    rate_bayes=round(record.bayesian_win_rate(self.global_stats["average_wins"], self.global_stats["average_plays"]) * 100, 2),  # type: ignore
                )
                for rank, (card, record) in enumerate(self.game_card_records.items())
            }

        return self.outputs[card]


class OpeningHandRawWinRate(CardRawWinRate):
    def game_log_cards(self, log: GameLog) -> dict[int, set[str]]:
        game_cards: defaultdict[int, set[str]] = defaultdict(lambda: set())
        for player_id, hand_cards in log.data.opening_hands.items():
            hand_card_names = [card.name for card in hand_cards]
            game_cards[player_id] = game_cards[player_id].union(hand_card_names)

        return game_cards
