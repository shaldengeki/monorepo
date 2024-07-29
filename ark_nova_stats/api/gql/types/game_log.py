import json
from typing import Any, Optional, Type

from graphql import (
    GraphQLArgument,
    GraphQLField,
    GraphQLInt,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLString,
)

from ark_nova_stats.bga_log_parser.game_log import GameLog as ParsedGameLog
from ark_nova_stats.config import app, db
from ark_nova_stats.models import GameLog as GameLogModel
from ark_nova_stats.models import GameParticipation as GameParticipationModel
from ark_nova_stats.models import User as UserModel


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
        "bgaTableId": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="ID of original table on BGA.",
            resolve=lambda game_log, info, **args: game_log.bga_table_id,
        ),
    }


game_log_type = GraphQLObjectType(
    "GameLog",
    description="A game log entry.",
    fields=game_log_fields,
)


def fetch_game_log(
    game_log: Type[GameLogModel], params: dict[str, Any]
) -> Optional[GameLogModel]:
    return (game_log.query.filter(game_log.id == params["id"])).first()


game_log_filters: dict[str, GraphQLArgument] = {
    "id": GraphQLArgument(
        GraphQLNonNull(GraphQLInt),
        description="ID of the game log.",
    ),
}


def game_log_field(game_log: type[GameLogModel]) -> GraphQLField:
    return GraphQLField(
        game_log_type,
        args=game_log_filters,
        resolve=lambda root, info, **args: fetch_game_log(game_log, args),
    )


def submit_game_logs(
    game_log_model: Type[GameLogModel],
    args: dict[str, Any],
) -> GameLogModel:
    json_logs = json.loads(args["logs"])
    parsed_logs = ParsedGameLog(**json_logs)

    table_ids = set(l.table_id for l in parsed_logs.data.logs)
    if len(table_ids) != 1:
        raise RuntimeError(
            f"Log is invalid: there must be exactly one table_id per game log, found: {table_ids}"
        )

    log = GameLogModel(bga_table_id=list(table_ids)[0], log=args["logs"])

    if app.config["TESTING"] == True:
        log.id = 1
    else:
        db.session.add(log)

        # Add users if not present.
        present_users = UserModel.query.filter(
            UserModel.bga_id.in_([user.id for user in log.users])
        ).all()

        users_to_create = (
            user
            for user in log.users
            if not any(present.bga_id == user.bga_id for present in present_users)
        )

        for user in users_to_create:
            db.session.add(
                UserModel(  # type: ignore
                    bga_id=user.id,
                    name=user.name,
                    avatar=user.avatar,
                )
            )

        # Now create a game participation for each user.
        for user in log.users:
            log_user = next(u for u in parsed_logs.data.players if u.id == user.bga_id)
            db.session.add(
                GameParticipationModel(  # type: ignore
                    user=user,
                    color=log_user.color,
                    game_log=log,
                )
            )

        db.session.commit()

    return log


def submit_game_logs_field(
    game_log_model: Type[GameLogModel],
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
