#!/usr/bin/env python3

import json
from collections import Counter
from pathlib import Path
from typing import Iterator

from python.runfiles import Runfiles

from ark_nova_stats.bga_log_parser.game_log import GameLog


def list_game_datafiles() -> Iterator[Path]:
    r = Runfiles.Create()
    known_game = Path(
        r.Rlocation(
            "_main/ark_nova_stats/emu_cup/data/539682665_sorryimlikethis_darcelmaw.json"
        )
    )
    return known_game.parent.glob("*.json")


def main() -> int:
    all_cards: Counter[str] = Counter()
    for p in list_game_datafiles():
        print(p)
        with open(p, "r") as f:
            log = GameLog(**json.loads(f.read().strip()))
        game_cards = set(
            event_data.args["card_name"]
            for event in log.data.logs
            for event_data in event.data
            if "card_name" in event_data.args
        )
        all_cards.update(game_cards)

    print("Most common cards:")
    for card, count in all_cards.most_common(20):
        print(f"  - {card}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
