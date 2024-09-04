import dataclasses


@dataclasses.dataclass
class PlayerELOs:
    name: str
    prior_elo: int
    new_elo: int
    prior_arena_elo: int
    new_arena_elo: int
