import json
import sys

import pytest
from python.runfiles import Runfiles

from ark_nova_stats.bga_log_parser.game_log import GameLog, GameLogEventData


class TestGameLog:
    def test_parses_sample_game(self):
        r = Runfiles.Create()
        sample_game_fixture = r.Rlocation(
            "_main/ark_nova_stats/bga_log_parser/fixtures/sample_game.log.json"
        )
        with open(sample_game_fixture, "r") as sample_game_logfile:
            game_log = json.loads(sample_game_logfile.read().strip())

        x = GameLog(**game_log)

        assert 1 == x.status
        assert 1098 == len(x.data.logs)
        assert "Baboude" == x.data.players[0].name
        assert "sorryimlikethis" == x.data.players[1].name
        assert 537650395 == x.data.logs[0].table_id
        assert 1 == x.data.logs[0].move_id
        assert 1721046021 == x.data.logs[0].time
        assert x.winner is not None and "sorryimlikethis" == x.winner.name


class TestGameLogEventData:
    def test_is_play_event_returns_true_for_play_action(self):
        r = Runfiles.Create()
        play_event_fixture = r.Rlocation(
            "_main/ark_nova_stats/bga_log_parser/fixtures/play_event.log.json"
        )
        with open(play_event_fixture, "r") as play_event_logfile:
            play_log = json.loads(play_event_logfile.read().strip())

        x = GameLogEventData(**play_log)
        assert x.is_play_action

    def test_is_play_event_returns_false_for_other_actions(self):
        r = Runfiles.Create()
        non_play_event_fixture = r.Rlocation(
            "_main/ark_nova_stats/bga_log_parser/fixtures/non_play_event.log.json"
        )
        with open(non_play_event_fixture, "r") as non_play_event_logfile:
            non_play_log = json.loads(non_play_event_logfile.read().strip())

        x = GameLogEventData(**non_play_log)
        assert not x.is_play_action


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
