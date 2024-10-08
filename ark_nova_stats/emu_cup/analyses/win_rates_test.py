import sys

import pytest

from ark_nova_stats.emu_cup.analyses.win_rates import CardRawWinRate


class TestCardRawWinRate:
    def test_returns_empty_when_no_logs_provided(self):
        raw_win_rate = CardRawWinRate()
        with pytest.raises(KeyError):
            raw_win_rate.output("no such card")

        assert 0 == len(raw_win_rate.all_cards)
        assert 0 == len(raw_win_rate.game_card_records)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
