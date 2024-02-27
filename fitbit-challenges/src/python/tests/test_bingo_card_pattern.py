import pytest

from ..bingo_card_pattern import BingoCardPattern, USABLE_PATTERNS


class EmptyPattern(BingoCardPattern):
    @property
    def pattern(self) -> list[list[int]]:
        return [[]]


class SingleEntryPattern(BingoCardPattern):
    @property
    def pattern(self) -> list[list[int]]:
        return [[0]]


class TwoEntryPattern(BingoCardPattern):
    @property
    def pattern(self) -> list[list[int]]:
        return [[0, 1]]


class TwoByTwoPattern(BingoCardPattern):
    @property
    def pattern(self) -> list[list[int]]:
        return [
            [0, 1],
            [1, 0],
        ]


class FiveByFivePattern(BingoCardPattern):
    @property
    def pattern(self) -> list[list[int]]:
        return [
            [1, 0, 1, 1, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 1, 1, 1],
        ]


class TestBingoCardPattern:
    def test_required_coordinate_raises_error_for_invalid_coordinate(self) -> None:
        p: BingoCardPattern = EmptyPattern()
        with pytest.raises(IndexError):
            p.required_coordinate(0, 0)

        p = FiveByFivePattern()
        with pytest.raises(IndexError):
            p.required_coordinate(-1, 0)
        with pytest.raises(IndexError):
            p.required_coordinate(0, -1)
        with pytest.raises(IndexError):
            p.required_coordinate(-1, -1)
        with pytest.raises(IndexError):
            p.required_coordinate(5, 0)
        with pytest.raises(IndexError):
            p.required_coordinate(0, 5)
        with pytest.raises(IndexError):
            p.required_coordinate(5, 5)

    def test_required_coordinate_true_for_required_coordinate(self) -> None:
        p = FiveByFivePattern()
        assert p.required_coordinate(0, 0)
        assert p.required_coordinate(2, 1)
        assert p.required_coordinate(4, 2)
        assert p.required_coordinate(0, 3)
        assert p.required_coordinate(4, 4)

    def test_required_coordinate_false_for_nonrequired_coordinate(self) -> None:
        p = FiveByFivePattern()
        assert not p.required_coordinate(1, 0)
        assert not p.required_coordinate(3, 1)
        assert not p.required_coordinate(1, 2)
        assert not p.required_coordinate(3, 3)
        assert not p.required_coordinate(1, 4)

    def test_number_of_required_tiles(self) -> None:
        p: BingoCardPattern = EmptyPattern()
        assert 0 == p.number_of_required_tiles

        p = SingleEntryPattern()
        assert 0 == p.number_of_required_tiles

        p = TwoEntryPattern()
        assert 1 == p.number_of_required_tiles

        p = TwoByTwoPattern()
        assert 2 == p.number_of_required_tiles

        p = FiveByFivePattern()
        assert 17 == p.number_of_required_tiles

    def test_number_of_tiles(self) -> None:
        p: BingoCardPattern = EmptyPattern()
        assert 0 == p.number_of_tiles

        p = SingleEntryPattern()
        assert 1 == p.number_of_tiles

        p = TwoEntryPattern()
        assert 2 == p.number_of_tiles

        p = TwoByTwoPattern()
        assert 4 == p.number_of_tiles

        p = FiveByFivePattern()
        assert 25 == p.number_of_tiles


class TestUsablePatterns:
    def test_at_least_one_usable_pattern(self) -> None:
        assert len(USABLE_PATTERNS) > 0

    def test_usable_patterns_all_have_required_tiles(self) -> None:
        for pattern in USABLE_PATTERNS:
            assert pattern().number_of_required_tiles > 0
