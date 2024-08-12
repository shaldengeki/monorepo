class BGALogParserError(BaseException):
    pass


class NonArkNovaReplayError(BGALogParserError):
    pass


class PlayerNotFoundError(BGALogParserError):
    pass
