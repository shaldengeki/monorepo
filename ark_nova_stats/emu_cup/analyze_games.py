#!/usr/bin/env python3

import dataclasses
import json
from collections import Counter
from pathlib import Path
from typing import Iterator, Optional

from python.runfiles import Runfiles

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


def main() -> int:
    all_cards: Counter[str] = Counter()
    winner_cards: Counter[str] = Counter()
    loser_cards: Counter[str] = Counter()

    event_logs: set[str] = set()
    skipped_event_logs: set[str] = set()
    game_card_records: dict[str, CardRecord] = {}

    for p in list_game_datafiles():
        with open(p, "r") as f:
            log = GameLog(**json.loads(f.read().strip()))

        if not log.table_id in EMU_CUP_GAME_TABLE_IDS:
            continue

        print(p)
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

        for card in game_cards:
            if card not in game_card_records:
                game_card_records[card] = CardRecord(card_name=card)

        for card in game_winner_cards:
            game_card_records[card].wins += 1
        for card in game_loser_cards:
            game_card_records[card].losses += 1

    # print("# Most common cards:")
    # for card, count in all_cards.most_common(15):
    #     print(f"- {card}: {count}")
    # print("")

    # print("# Most commonly played by winner:")
    # for card, count in winner_cards.most_common(15):
    #     print(f"- {card}: {count}")
    # print("")

    # print("# Most commonly played by loser:")
    # for card, count in loser_cards.most_common(50):
    #     print(f"- {card}: {count}")
    # print("")

    global_stats = [
        (record.wins, record.wins + record.losses)
        for _, record in game_card_records.items()
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
        for card, record in game_card_records.items()
        if record.win_rate is not None
    ]

    print(f"# Card win rates:")
    print("")
    print(
        'We define "win rate" as "if a player played this card, how frequently did they end up winning the game?"'
    )
    print("")
    print("Uses the data at https://arknova.ouguo.us.")
    print("")
    print(
        f"The average card has a win rate of {round(average_wins * 1.0 / average_plays * 100)}%, with {round(average_wins, 1)} wins over {round(average_plays, 1)} plays"
    )
    print("| Rank | Card | Win rate | Plays | Win rate (Bayes) |")
    print("|------|------|----------|-------|------------------|")
    rank = 1
    for card, rate, plays, rate_bayes in sorted(
        win_rates, key=lambda x: x[3], reverse=True
    ):
        print(f"| {rank} | {card} | {rate}% | {plays} | {rate_bayes}% |")
        rank += 1
    print("")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
