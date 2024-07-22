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
    winner_cards: Counter[str] = Counter()
    loser_cards: Counter[str] = Counter()

    event_logs: set[str] = set()
    skipped_event_logs: set[str] = set()

    for p in list_game_datafiles():
        print(p)
        with open(p, "r") as f:
            log = GameLog(**json.loads(f.read().strip()))

        winner = log.winner

        game_cards: set[str] = set()
        game_winner_cards: set[str] = set()
        game_loser_cards: set[str] = set()
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
        all_cards.update(game_cards)
        winner_cards.update(game_winner_cards)
        loser_cards.update(game_loser_cards)

    print("Most common cards:")
    for card, count in all_cards.most_common(10):
        print(f"- {card}: {count}")

    print("Most commonly played by winner:")
    for card, count in winner_cards.most_common(10):
        print(f"- {card}: {count}")

    print("Most commonly played by loser:")
    for card, count in loser_cards.most_common(10):
        print(f"- {card}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
