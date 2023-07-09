class BingoCardPattern:
    @property
    def pattern(self) -> list[list[int]]:
        raise NotImplementedError

    def required_coordinate(self, x: int, y: int) -> bool:
        return bool(self.pattern[y][x] == 1)

    @property
    def number_of_required_tiles(self) -> int:
        return sum(val for row in self.pattern for val in row)

    @property
    def number_of_tiles(self) -> int:
        return sum(len(row) for row in self.pattern)


class TenBingoCardPattern(BingoCardPattern):
    @property
    def pattern(self) -> list[list[int]]:
        return [
            [1, 0, 1, 1, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 1, 1, 1],
        ]


class SailboatBingoCardPattern(BingoCardPattern):
    @property
    def pattern(self) -> list[list[int]]:
        return [
            [0, 0, 1, 0, 0],
            [0, 1, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0],
        ]


class HouseBingoCardPattern(BingoCardPattern):
    @property
    def pattern(self) -> list[list[int]]:
        return [
            [0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0],
            [1, 1, 1, 1, 1],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0],
        ]


USABLE_PATTERNS = [TenBingoCardPattern, SailboatBingoCardPattern, HouseBingoCardPattern]
