import sys

import pytest

from ark_nova_stats.emu_cup.analyze_games import CardWinRateELOAdjusted


class TestCardWinRateELOAdjusted:
    def test_returns_empty_when_no_logs_provided(self):
        elo_adjusted = CardWinRateELOAdjusted()
        with pytest.raises(KeyError):
            elo_adjusted.output("no such card")

        assert 0 == len(elo_adjusted.all_cards)
        assert 0 == len(elo_adjusted.game_card_records)

    pass


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
