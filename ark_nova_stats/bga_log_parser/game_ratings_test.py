import sys
from pathlib import Path

import pytest
from python.runfiles import Runfiles  # type: ignore

from ark_nova_stats.bga_log_parser.game_ratings import parse_ratings


def load_data_from_fixture_file(filename: str) -> str:
    r = Runfiles.Create()
    fixture_file_path = r.Rlocation(
        str(Path("_main") / "ark_nova_stats" / "bga_log_parser" / "fixtures" / filename)
    )
    with open(fixture_file_path, "r") as fixture_file:
        return fixture_file.read().strip()


class TestGameLog:
    def test_parses_sample_ratings(self):
        raw_ratings = load_data_from_fixture_file("sample_game_ratings.json")
        ratings = parse_ratings(raw_ratings)
        assert 1 == ratings.status
        assert 2 == len(ratings.data.players_results)
        assert 2 == len(ratings.data.players_current_ratings)
        assert 2 == len(ratings.data.players_elo_rating_update)
        assert 2 == len(ratings.data.players_arena_rating_update)

    def test_parses_non_arena_ratings(self):
        raw_ratings = load_data_from_fixture_file("ratings_non_arena.json")
        ratings = parse_ratings(raw_ratings)
        assert 1 == ratings.status
        assert 2 == len(ratings.data.players_results)
        assert 2 == len(ratings.data.players_current_ratings)
        assert 2 == len(ratings.data.players_elo_rating_update)
        assert 0 == len(ratings.data.players_arena_rating_update)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
