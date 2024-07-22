import json
import sys
from pathlib import Path

import pytest
from python.runfiles import Runfiles

from ark_nova_stats.bga_log_parser.game_log import GameLog, GameLogEventData


def load_data_from_fixture_file(filename: str) -> dict:
    r = Runfiles.Create()
    fixture_file_path = r.Rlocation(
        str(Path("_main") / "ark_nova_stats" / "bga_log_parser" / "fixtures" / filename)
    )
    with open(fixture_file_path, "r") as fixture_file:
        return json.loads(fixture_file.read().strip())


class TestGameLog:
    def test_parses_sample_game(self):
        game_log = load_data_from_fixture_file("sample_game.log.json")
        x = GameLog(**game_log)

        assert 1 == x.status
        assert 1098 == len(x.data.logs)
        assert "Baboude" == x.data.players[0].name
        assert "sorryimlikethis" == x.data.players[1].name
        assert 537650395 == x.data.logs[0].table_id
        assert 1 == x.data.logs[0].move_id
        assert 1721046021 == x.data.logs[0].time
        assert x.winner is not None and "sorryimlikethis" == x.winner.name
        assert not x.is_tie

    def test_detects_tie(self):
        game_log = load_data_from_fixture_file("tie.log.json")
        x = GameLog(**game_log)
        assert x.is_tie


class TestGameLogEventData:
    def test_is_play_event_returns_true_for_play_action(self):
        play_log = load_data_from_fixture_file("play_event.log.json")
        x = GameLogEventData(**play_log)
        assert x.is_play_action

    def test_is_play_event_returns_false_for_other_actions(self):
        non_play_log = load_data_from_fixture_file("non_play_event.log.json")
        x = GameLogEventData(**non_play_log)
        assert not x.is_play_action


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
