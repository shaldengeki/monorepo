from typing import Any, Iterable, Optional, Type

from graphql import (
    GraphQLArgument,
    GraphQLField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLString,
)
from sqlalchemy import asc

from ark_nova_stats.api.gql.types.game_log import game_log_type, user_type
from ark_nova_stats.bga_log_parser.game_ratings import parse_ratings
from ark_nova_stats.config import app, db
from ark_nova_stats.models import GameLog as GameLogModel
from ark_nova_stats.models import GameRating as GameRatingModel


def game_rating_game_log_resolver(
    game_rating: GameRatingModel, info, **args
) -> GameLogModel:
    return game_rating.game_log


def game_rating_prior_elo_resolver(
    game_rating: GameRatingModel, info, **args
) -> Optional[int]:
    return game_rating.prior_elo


def game_rating_new_elo_resolver(
    game_rating: GameRatingModel, info, **args
) -> Optional[int]:
    return game_rating.new_elo


def game_rating_prior_arena_elo_resolver(
    game_rating: GameRatingModel, info, **args
) -> Optional[int]:
    return game_rating.prior_arena_elo


def game_rating_new_arena_elo_resolver(
    game_rating: GameRatingModel, info, **args
) -> Optional[int]:
    return game_rating.new_arena_elo


def game_rating_fields() -> dict[str, GraphQLField]:
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="Unique ID of this game rating result.",
        ),
        "gameLog": GraphQLField(
            GraphQLNonNull(game_log_type),
            description="Game log that this rating change corresponds to.",
            resolve=game_rating_game_log_resolver,
        ),
        "user": GraphQLField(
            GraphQLNonNull(user_type),
            description="User that this rating change corresponds to.",
        ),
        "priorElo": GraphQLField(
            GraphQLInt,
            description="User's ELO before this match.",
            resolve=game_rating_prior_elo_resolver,
        ),
        "newElo": GraphQLField(
            GraphQLInt,
            description="User's ELO after this match.",
            resolve=game_rating_new_elo_resolver,
        ),
        "priorArenaElo": GraphQLField(
            GraphQLInt,
            description="User's Arena ELO before this match.",
            resolve=game_rating_prior_arena_elo_resolver,
        ),
        "newArenaElo": GraphQLField(
            GraphQLInt,
            description="User's Arena ELO after this match.",
            resolve=game_rating_new_arena_elo_resolver,
        ),
    }


game_rating_type = GraphQLObjectType(
    "GameRating",
    description="A game rating entry.",
    fields=game_rating_fields,
)


def compute_arena_elo_from_rating(rating: float) -> float:
    # Arena ratings look like: 201.1234
    # where 201 determines your league, and 1234 is the actual ELO.
    # So we transform that to 1234.
    leading_arena_elo_digits = int(rating)
    return 10_000 * (rating - leading_arena_elo_digits)


def submit_game_ratings(
    game_rating_model: Type[GameRatingModel],
    args: dict[str, Any],
) -> list[GameRatingModel]:
    table_id = int(args["tableId"])
    parsed_ratings = parse_ratings(args["ratings"])

    ratings = []
    for (
        player_id,
        elo_rating_update,
    ) in parsed_ratings.data.players_elo_rating_update.items():
        rating = game_rating_model(
            bga_table_id=table_id,
            user_id=player_id,
            prior_elo=round(
                elo_rating_update.new_elo_rating - elo_rating_update.tot_elo_delta
            ),
            new_elo=round(elo_rating_update.new_elo_rating),
        )

        if player_id in parsed_ratings.data.players_arena_rating_update:
            arena_rating_update = parsed_ratings.data.players_arena_rating_update[
                player_id
            ]
            new_arena_elo = compute_arena_elo_from_rating(
                arena_rating_update.new_arena_rating
            )
            arena_elo_delta = arena_rating_update.real_arena_elo_delta
            rating.prior_arena_elo = round(new_arena_elo - arena_elo_delta)
            rating.new_arena_elo = round(new_arena_elo)

        if app.config["TESTING"] == True:
            rating.id = 1
            ratings.append(rating)
        else:
            # Only try to create this if it doesn't already exist.
            if (
                db.session.execute(
                    db.select(game_rating_model)
                    .filter(game_rating_model.bga_table_id == table_id)
                    .filter(game_rating_model.user_id == player_id)
                    .count()
                ).scalar_one()
                == 0
            ):
                db.session.add(rating)
                ratings.append(rating)

    if app.config["TESTING"] != True:
        db.session.commit()

    return ratings


def submit_game_ratings_field(
    game_rating_model: Type[GameRatingModel],
) -> GraphQLField:
    return GraphQLField(
        GraphQLNonNull(GraphQLList(game_rating_type)),
        description="Submit ratings updates for a game.",
        args={
            "ratings": GraphQLArgument(
                GraphQLNonNull(GraphQLString),
                description="JSON-encoded representation of the game's rating update.",
            ),
            "tableId": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="BGA table ID for the game.",
            ),
        },
        resolve=lambda root, info, **args: submit_game_ratings(game_rating_model, args),
    )


def fetch_game_ratings(
    game_rating_model: Type[GameRatingModel], args: dict
) -> Iterable[GameRatingModel]:
    query = db.select(game_rating_model)
    table_ids = [int(i) for i in args["bgaTableIds"]]
    query = query.where(game_rating_model.bga_table_id.in_(table_ids))

    return db.session.execute(
        query.order_by(asc(game_rating_model.bga_table_id)).all()
    ).scalars()


fetch_game_ratings_filters: dict[str, GraphQLArgument] = {
    "bgaTableIds": GraphQLArgument(
        GraphQLNonNull(GraphQLList(GraphQLInt)),
        description="List of BGA table IDs to fetch.",
    ),
}


def fetch_game_ratings_field(
    game_rating_model: Type[GameRatingModel],
) -> GraphQLField:
    return GraphQLField(
        GraphQLNonNull(GraphQLList(game_rating_type)),
        description="Retrieves game ratings for one or more games.",
        args=fetch_game_ratings_filters,
        resolve=lambda root, info, **args: fetch_game_ratings(game_rating_model, args),
    )
