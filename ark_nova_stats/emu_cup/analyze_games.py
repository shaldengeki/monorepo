#!/usr/bin/env python3

import csv
import datetime
import json
import os
import sys
from pathlib import Path

from python.runfiles import Runfiles  # type: ignore

from ark_nova_stats.bga_log_parser.exceptions import StatsNotSetError
from ark_nova_stats.bga_log_parser.game_log import GameLog
from ark_nova_stats.emu_cup.analyses.elo_adjusted import (
    CardWinRateELOAdjusted,
    OpeningHandWinRateELOAdjusted,
)
from ark_nova_stats.emu_cup.analyses.win_rates import (
    CardRawWinRate,
    OpeningHandRawWinRate,
)
from ark_nova_stats.emu_cup.player_elos import PlayerELOs
from ark_nova_stats.emu_cup.tables import EMU_CUP_GAME_TABLE_IDS


def list_game_datafiles() -> list[Path]:
    r = Runfiles.Create()
    known_game = Path(
        r.Rlocation(
            "_main/ark_nova_stats/emu_cup/data/nonempty.json"
        )
    )
    return sorted([f for f in known_game.parent.glob("*.json") if f.name != 'nonempty.json'])


def main(working_dir: str) -> int:
    raw_win_rates = CardRawWinRate()
    opening_hand_raw_win_rates = OpeningHandRawWinRate()
    elo_win_rates = CardWinRateELOAdjusted()
    opening_hand_elo_win_rates = OpeningHandWinRateELOAdjusted()

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
            elos: dict[int, PlayerELOs] = {
                int(user_id): PlayerELOs(id=user_id, **vals)
                for user_id, vals in parsed_file["elos"].items()
            }

        raw_win_rates.process_game(log)
        opening_hand_raw_win_rates.process_game(log)

        if not elos:
            continue
        try:
            elo_win_rates.process_game(log, elos)
            opening_hand_elo_win_rates.process_game(log, elos)
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
            "opening_hand_count_raw",
            "opening_hand_win_rate_raw",
            "opening_hand_win_rate_raw_bayes",
            "play_count_wae",
            "wins_above_expected",
            "wins_above_expected_bayes",
            "opening_hand_count_wae",
            "opening_hand_wins_above_expected",
            "opening_hand_wins_above_expected_bayes",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for card in raw_win_rates.all_cards:
            raw_output = raw_win_rates.output(card)
            elo_output = elo_win_rates.output(card)
            row = {
                "card": card,
                "play_count_raw": raw_output.plays,
                "win_rate_raw": raw_output.rate,
                "win_rate_raw_bayes": raw_output.rate_bayes,
            }
            if card in opening_hand_raw_win_rates.all_cards:
                opening_hand_raw_output = opening_hand_raw_win_rates.output(card)
                row.update(
                    {
                        "opening_hand_count_raw": opening_hand_raw_output.plays,
                        "opening_hand_win_rate_raw": opening_hand_raw_output.rate,
                        "opening_hand_win_rate_raw_bayes": opening_hand_raw_output.rate_bayes,
                    }
                )

            row.update(
                {
                    "play_count_wae": elo_output.plays,
                    "wins_above_expected": elo_output.rate,
                    "wins_above_expected_bayes": elo_output.rate_bayes,
                }
            )

            if card in opening_hand_elo_win_rates.all_cards:
                opening_hand_elo_output = opening_hand_elo_win_rates.output(card)
                row.update(
                    {
                        "opening_hand_count_wae": opening_hand_elo_output.plays,
                        "opening_hand_wins_above_expected": opening_hand_elo_output.rate,
                        "opening_hand_wins_above_expected_bayes": opening_hand_elo_output.rate_bayes,
                    }
                )

            writer.writerow(row)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
