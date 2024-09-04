#!/usr/bin/env python3

import csv
import datetime
import json
import os
import sys
from pathlib import Path

from python.runfiles import Runfiles

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


def list_game_datafiles() -> list[Path]:
    r = Runfiles.Create()
    known_game = Path(
        r.Rlocation(
            "_main/ark_nova_stats/emu_cup/data/531081985_Sirhk_sorryimlikethis_Awesometothemax_Pogstar.json"
        )
    )
    return sorted(known_game.parent.glob("*.json"))


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
            elos: dict[str, PlayerELOs] = {
                name: PlayerELOs(name=name, **vals)
                for name, vals in parsed_file["elos"].items()
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
