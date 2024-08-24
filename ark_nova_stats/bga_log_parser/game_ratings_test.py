import sys
from pathlib import Path

import pytest
from google.protobuf.json_format import Parse
from python.runfiles import Runfiles

from ark_nova_stats.bga_log_parser.proto.ratings_pb2 import GameRatings


def load_data_from_fixture_file(filename: str) -> str:
    r = Runfiles.Create()
    fixture_file_path = r.Rlocation(
        str(Path("_main") / "ark_nova_stats" / "bga_log_parser" / "fixtures" / filename)
    )
    with open(fixture_file_path, "r") as fixture_file:
        return fixture_file.read().strip()


class TestGameLog:
    def test_parses_sample_ratings(self):
        game_ratings = load_data_from_fixture_file("sample_game_ratings.json")
        ratings = Parse(game_ratings, GameRatings(), ignore_unknown_fields=True)
        assert 1 == ratings.status
        assert 2 == len(ratings.data.players_results)
        assert 2 == len(ratings.data.players_current_ratings)
        assert 2 == len(ratings.data.players_elo_rating_update)
        assert 2 == len(ratings.data.players_arena_rating_update)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
