class BGALogParserError(BaseException):
    pass


class MoveNotSetError(BGALogParserError):
    pass


class NonArkNovaReplayError(BGALogParserError):
    pass


class PlayerNotFoundError(BGALogParserError):
    pass
