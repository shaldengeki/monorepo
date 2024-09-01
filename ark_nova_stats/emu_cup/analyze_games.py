#!/usr/bin/env python3

import csv
import dataclasses
import datetime
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Iterator, Optional

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


@dataclasses.dataclass
class CardRawWinRateOutput:
    rank: int
    card: str
    rate: int
    plays: int
    rate_bayes: int


class CardRawWinRate:
    def __init__(self):
        self.all_cards: Counter[str] = Counter()
        self.winner_cards: Counter[str] = Counter()
        self.loser_cards: Counter[str] = Counter()
        self.game_card_records: dict[str, CardRecord] = {}
        self.global_stats = None
        self.outputs = None

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

    def output(self, card) -> CardRawWinRateOutput:
        if self.global_stats is None:
            global_stats = [
                (record.wins, record.wins + record.losses)
                for _, record in self.game_card_records.items()
            ]
            self.global_stats = {}
            self.global_stats["total_wins"] = sum(wins for wins, _ in global_stats)
            self.global_stats["average_wins"] = (
                self.global_stats["total_wins"] * 1.0 / len(global_stats)
            )
            self.global_stats["total_plays"] = sum(plays for _, plays in global_stats)
            self.global_stats["average_plays"] = (
                self.global_stats["total_plays"] * 1.0 / len(global_stats)
            )

        if self.outputs is None:
            self.outputs = {
                card: CardRawWinRateOutput(
                    rank=rank + 1,
                    card=card,
                    rate=0 if record.win_rate is None else round(record.win_rate * 100),
                    plays=record.wins + record.losses,
                    rate_bayes=round(record.bayesian_win_rate(self.global_stats["average_wins"], self.global_stats["average_plays"]) * 100),  # type: ignore
                )
                for rank, (card, record) in enumerate(self.game_card_records.items())
            }

        return self.outputs[card]


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


@dataclasses.dataclass
class CardWinRateELOAdjustedOutput:
    rank: int
    card: str
    rate: float
    plays: int
    rate_bayes: float


class CardWinRateELOAdjusted:
    def __init__(self):
        self.all_cards: Counter[str] = Counter()
        self.game_card_records: dict[str, CardELORecord] = {}
        self.average_plays = None
        self.outputs = None

    def process_game(self, log: GameLog, elos: dict[str, PlayerELOs]) -> None:
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
            if log.is_tie:
                self.game_card_records[card].add_points(0.5 - loser_winrate)
            else:
                self.game_card_records[card].add_points(0 - loser_winrate)

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


def main(working_dir: str) -> int:
    raw_win_rates = CardRawWinRate()
    elo_win_rates = CardWinRateELOAdjusted()

    for p in list_game_datafiles():
        # path_parts = p.name.split("_")
        # if int(path_parts[0]) not in EMU_CUP_GAME_TABLE_IDS:
        #     continue

        print(p)
        with open(p, "r") as f:
            parsed_file = json.loads(f.read().strip())
            try:
                log = GameLog(**parsed_file["log"])
            except StatsNotSetError:
                print(f"{p} doesn't have stats set!")
                continue
            elos: dict[str, PlayerELOs] = {
                name: PlayerELOs(name=name, **vals)
                for name, vals in parsed_file["elos"].items()
            }

        raw_win_rates.process_game(log)
        if not elos:
            continue
        try:
            elo_win_rates.process_game(log, elos)
        except Exception as e:
            print(f"Failed to process {p}: {e}")
            continue

    os.chdir(working_dir)

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(f"ark-card-war-{date}.csv", "w") as csvfile:
        fieldnames = [
            "card",
            "play_count_raw",
            "win_rate_raw",
            "win_rate_raw_bayes",
            "play_count_wae",
            "wins_above_expected",
            "wins_above_expected_bayes",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for card in raw_win_rates.all_cards:
            raw_output = raw_win_rates.output(card)
            elo_output = elo_win_rates.output(card)

            writer.writerow(
                {
                    "card": card,
                    "play_count_raw": raw_output.plays,
                    "win_rate_raw": raw_output.rate,
                    "win_rate_raw_bayes": raw_output.rate_bayes,
                    "play_count_wae": elo_output.plays,
                    "wins_above_expected": elo_output.rate,
                    "wins_above_expected_bayes": elo_output.rate_bayes,
                }
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
