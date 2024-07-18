import json
from typing import Any, Optional, Type

from flask import Flask
from graphql import (
    GraphQLArgument,
    GraphQLField,
    GraphQLInt,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLString,
)

from ark_nova_stats.config import app, db
from ark_nova_stats.models import GameLog, GameLogContainerJSON


def game_log_fields() -> dict[str, GraphQLField]:
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The id of the game log.",
        ),
        "log": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The game log.",
        ),
    }


game_log_type = GraphQLObjectType(
    "GameLog",
    description="A game log entry.",
    fields=game_log_fields,
)


def fetch_game_log(
    game_log: Type[GameLog], params: dict[str, Any]
) -> Optional[GameLog]:
    return (game_log.query.filter(game_log.id == params["id"])).first()


game_log_filters: dict[str, GraphQLArgument] = {
    "id": GraphQLArgument(
        GraphQLNonNull(GraphQLInt),
        description="ID of the game log.",
    ),
}


def game_log_field(game_log: type[GameLog]) -> GraphQLField:
    return GraphQLField(
        game_log_type,
        args=game_log_filters,
        resolve=lambda root, info, **args: fetch_game_log(game_log, args),
    )


def submit_game_logs(
    game_log_model: Type[GameLog],
    args: dict[str, Any],
) -> GameLog:
    json_logs = json.loads(args["logs"])
    parsed_logs = GameLogContainerJSON(**json_logs)

    # For now, just store the literal log string.
    log = GameLog(log=args["logs"])

    if app.config["TESTING"] == True:
        log.id = 1
    else:
        db.session.add(log)
        db.session.commit()

    return log


def submit_game_logs_field(
    game_log_model: Type[GameLog],
) -> GraphQLField:
    return GraphQLField(
        game_log_type,
        description="Submit logs for a game.",
        args={
            "logs": GraphQLArgument(
                GraphQLNonNull(GraphQLString),
                description="JSON-encoded representation of game logs.",
            ),
        },
        resolve=lambda root, info, **args: submit_game_logs(game_log_model, args),
    )
