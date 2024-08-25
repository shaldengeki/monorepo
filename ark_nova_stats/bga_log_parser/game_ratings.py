import json

from google.protobuf.json_format import ParseDict

from ark_nova_stats.bga_log_parser.proto.ratings_pb2 import GameRatings


def parse_ratings(raw_ratings: str) -> GameRatings:
    json_ratings = json.loads(raw_ratings)

    # Normally, for Arena games, we expect the rating update field to be a map.
    # Unfortunately, in the case of non-Arena games, BGA sends along a totally different type (a list).
    # This breaks our parsing, so we have to delete the field entirely.
    # Similar for friendly games!
    if (
        "data" in json_ratings
        and "players_elo_rating_update" in json_ratings["data"]
        and isinstance(json_ratings["data"]["players_elo_rating_update"], list)
    ):
        del json_ratings["data"]["players_elo_rating_update"]

    if (
        "data" in json_ratings
        and "players_arena_rating_update" in json_ratings["data"]
        and isinstance(json_ratings["data"]["players_arena_rating_update"], list)
    ):
        del json_ratings["data"]["players_arena_rating_update"]

    return ParseDict(json_ratings, GameRatings(), ignore_unknown_fields=True)
