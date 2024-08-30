#!/usr/bin/env python3

import dataclasses
import json
from collections import Counter
from pathlib import Path
from typing import Generator, Iterator, Optional

from python.runfiles import Runfiles

from ark_nova_stats.bga_log_parser.exceptions import StatsNotSetError
from ark_nova_stats.bga_log_parser.game_log import GameLog

EMU_CUP_GAME_TABLE_IDS = set(
    [
        539719810,
        539682665,
        539690819,
        539714189,
        539739367,
        539768389,
        539956725,
        540065264,
        540172423,
        540191201,
        540203937,
        540221827,
        540290164,
        540316010,
        540306709,
        540617341,
        540640875,
        540647292,
        540894619,
        540955752,
        540950947,
        541132564,
        541206562,
        541429802,
        541463814,
        541462291,
        541497323,
        541494297,
        541527117,
        541551348,
        541803532,
        541950717,
        541976632,
        542023324,
        542171714,
        542235867,
        542255543,
        542364386,
        542569160,
        542589556,
        542983232,
        543080510,
        543092478,
        543430761,
        543472681,
        543808017,
        543853166,
        543957417,
        544250311,
        544352216,
        544611344,
        545060181,
        545100776,
        545140355,
        545339082,
    ]
)


def list_game_datafiles() -> Iterator[Path]:
    r = Runfiles.Create()
    known_game = Path(
        r.Rlocation(
            "_main/ark_nova_stats/emu_cup/data/531081985_Sirhk_sorryimlikethis_Awesometothemax_Pogstar.json"
        )
    )
    return known_game.parent.glob("*.json")


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


class CardRawWinRate:
    def __init__(self):
        self.all_cards: Counter[str] = Counter()
        self.winner_cards: Counter[str] = Counter()
        self.loser_cards: Counter[str] = Counter()
        self.game_card_records: dict[str, CardRecord] = {}

    def process_game(self, log: GameLog) -> None:
        game_cards: set[str] = set()
        game_winner_cards: set[str] = set()
        game_loser_cards: set[str] = set()
        winner = log.winner

        for event in log.data.logs:
            for event_data in event.data:
                if not event_data.is_play_action:
                    continue

                card_names = event_data.played_card_names
                if card_names is None:
                    continue

                game_cards = game_cards.union(card_names)

                if log.is_tie:
                    continue

                if event_data.player is not None and winner is not None:
                    if event_data.player["id"] == winner.id:
                        game_winner_cards = game_winner_cards.union(card_names)
                    else:
                        game_loser_cards = game_loser_cards.union(card_names)

        self.all_cards.update(game_cards)
        self.winner_cards.update(game_winner_cards)
        self.loser_cards.update(game_loser_cards)

        for card in game_cards:
            if card not in self.game_card_records:
                self.game_card_records[card] = CardRecord(card_name=card)

        for card in game_winner_cards:
            self.game_card_records[card].wins += 1
        for card in game_loser_cards:
            self.game_card_records[card].losses += 1

    def output(self) -> Generator[str, None, None]:
        global_stats = [
            (record.wins, record.wins + record.losses)
            for _, record in self.game_card_records.items()
        ]
        total_wins = sum(wins for wins, _ in global_stats)
        average_wins = total_wins * 1.0 / len(global_stats)
        total_plays = sum(plays for _, plays in global_stats)
        average_plays = total_plays * 1.0 / len(global_stats)
        win_rates = [
            (
                card,
                round(record.win_rate * 100),
                record.wins + record.losses,
                round(record.bayesian_win_rate(average_wins, average_plays) * 100),  # type: ignore
            )
            for card, record in self.game_card_records.items()
            if record.win_rate is not None
        ]

        yield f"# Card win rates:"
        yield ""
        yield 'We define "win rate" as "if a player played this card, how frequently did they end up winning the game?"'
        yield ""
        yield "Uses the data at https://arknova.ouguo.us."
        yield ""
        yield f"The average card has a win rate of {round(average_wins * 1.0 / average_plays * 100)}%, with {round(average_wins, 1)} wins over {round(average_plays, 1)} plays"
        yield "| Rank | Card | Win rate | Plays | Win rate (Bayes) |"
        yield "|------|------|----------|-------|------------------|"
        rank = 1
        for card, rate, plays, rate_bayes in sorted(
            win_rates, key=lambda x: x[3], reverse=True
        ):
            yield f"| {rank} | {card} | {rate}% | {plays} | {rate_bayes}% |"
            rank += 1


@dataclasses.dataclass
class PlayerELOs:
    name: str
    prior_elo: int
    new_elo: int
    prior_arena_elo: int
    new_arena_elo: int


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


def probability_of_win(elo_1: int, elo_2: int) -> float:
    return 1.0 / (1 + pow(10, ((elo_2 - elo_1) / 400.0)))


class CardWinRateELOAdjusted:
    def __init__(self):
        self.all_cards: Counter[str] = Counter()
        self.game_card_records: dict[str, CardELORecord] = {}

    def process_game(self, log: GameLog, elos: dict[str, PlayerELOs]) -> None:
        if log.is_tie:
            print(f"Skipping log, is a tie")
            return

        game_cards: set[str] = set()
        game_winner_cards: set[str] = set()
        game_loser_cards: set[str] = set()
        winner = log.winner

        if winner is None:
            print(f"Skpping log, no winner")
            return

        if len(log.data.players) != 2:
            print(f"Skipping log, not a two-player game")

        winrates_by_id: dict[int, float] = {
            log.data.players[0].id: probability_of_win(
                elos[log.data.players[0].name].prior_elo,
                elos[log.data.players[1].name].prior_elo,
            ),
            log.data.players[1].id: probability_of_win(
                elos[log.data.players[1].name].prior_elo,
                elos[log.data.players[0].name].prior_elo,
            ),
        }

        winner_winrate = winrates_by_id[winner.id]
        loser_winrate = 1 - winner_winrate

        for event in log.data.logs:
            for event_data in event.data:
                if not event_data.is_play_action:
                    continue

                card_names = event_data.played_card_names
                if card_names is None:
                    continue

                game_cards = game_cards.union(card_names)

                if event_data.player is not None and winner is not None:
                    if event_data.player["id"] == winner.id:
                        game_winner_cards = game_winner_cards.union(card_names)
                    else:
                        game_loser_cards = game_loser_cards.union(card_names)

        self.all_cards.update(game_cards)

        for card in game_cards:
            if card not in self.game_card_records:
                self.game_card_records[card] = CardELORecord(card_name=card)

        for card in game_winner_cards:
            self.game_card_records[card].add_points(1 - winner_winrate)
        for card in game_loser_cards:
            self.game_card_records[card].add_points(0 - loser_winrate)

    def output(self) -> Generator[str, None, None]:
        average_plays = (
            1.0
            * sum(record.games for record in self.game_card_records.values())
            / len(self.game_card_records)
        )
        wins_above_replacement = [
            (
                card,
                round(record.avg_points * 100, 2),
                record.games,
                round(record.bayesian_avg_points(0, average_plays) * 100, 2),  # type: ignore
            )
            for card, record in self.game_card_records.items()
            if record.avg_points is not None
        ]

        yield f"# Card wins above replacement:"
        yield ""
        yield 'We define wins above replacement (WAR) as "if a player played this card, how much did they win a game more often than would be expected based on their ELO alone?"'
        yield ""
        yield "The last column is the card's WAR, with Bayesian smoothing applied. Basically, we mix in the average card's WAR (which is zero) into each card's data, which helps compensate for rarely-played cards."
        yield ""
        yield "Uses the data at https://arknova.ouguo.us."
        yield ""
        yield f"The average card was played {round(average_plays, 1)} times."
        yield "| Rank | Card | Wins above replacement | Plays | WAR (Bayes) |"
        yield "|------|------|------------------------|-------|-------------|"
        rank = 1
        for card, rate, plays, rate_bayes in sorted(
            wins_above_replacement, key=lambda x: x[3], reverse=True
        ):
            yield f"| {rank} | {card} | {rate}% | {plays} | {rate_bayes}% |"
            rank += 1


def main() -> int:
    raw_win_rates = CardRawWinRate()
    elo_win_rates = CardWinRateELOAdjusted()

    for p in list_game_datafiles():
        # path_parts = p.name.split("_")
        # if int(path_parts[0]) not in EMU_CUP_GAME_TABLE_IDS:
        #     continue

        with open(p, "r") as f:
            parsed_file = json.loads(f.read().strip())
            try:
                log = GameLog(**parsed_file["log"])
            except StatsNotSetError:
                print(f"{p} doesn't have stats set!")
                continue
            elos: dict[str, PlayerELOs] = {
                name: PlayerELOs(**vals) for name, vals in parsed_file["elos"].items()
            }

        raw_win_rates.process_game(log)
        elo_win_rates.process_game(log, elos)

    for l in raw_win_rates.output():
        print(l)

    for l in elo_win_rates.output():
        print(l)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
