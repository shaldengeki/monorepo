class BGALogParserError(BaseException):
    pass


class MoveNotSetError(BGALogParserError):
    pass


class StatsNotSetError(BGALogParserError):
    pass


class NonArkNovaReplayError(BGALogParserError):
    pass


class PlayerNotFoundError(BGALogParserError):
    pass
