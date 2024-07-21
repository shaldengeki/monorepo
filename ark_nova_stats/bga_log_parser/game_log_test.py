import json
import sys

import pytest
from python.runfiles import Runfiles

from ark_nova_stats.bga_log_parser.game_log import GameLog


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


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
