import sys

import pytest

from ark_nova_stats.api.gql.types.game_rating import compute_arena_elo_from_rating


def test_compute_arena_elo_from_rating_handles_bronze():
    assert round(compute_arena_elo_from_rating(0.1468)) == 1468


def test_compute_arena_elo_from_rating_handles_gold():
    assert round(compute_arena_elo_from_rating(209.1628)) == 1628


def test_compute_arena_elo_from_rating_handles_elite():
    assert round(compute_arena_elo_from_rating(501.1643)) == 1643


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
