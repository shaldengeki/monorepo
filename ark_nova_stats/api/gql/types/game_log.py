import json
import logging
from typing import Any, Optional, Type

from graphql import (
    GraphQLArgument,
    GraphQLField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLString,
)

from ark_nova_stats.bga_log_parser.game_log import GameLog as ParsedGameLog
from ark_nova_stats.config import app, db
from ark_nova_stats.models import GameLog as GameLogModel
from ark_nova_stats.models import GameParticipation as GameParticipationModel
from ark_nova_stats.models import User as UserModel


def game_log_bga_table_id_resolver(game_log: GameLogModel, info, **args) -> int:
    return game_log.bga_table_id


def game_log_users_resolver(game_log: GameLogModel, info, **args) -> list[UserModel]:
    return game_log.users


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
            resolve=game_log_bga_table_id_resolver,
        ),
        "users": GraphQLField(
            GraphQLNonNull(GraphQLList(user_type)),
            resolve=game_log_users_resolver,
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

    log = GameLogModel(bga_table_id=list(table_ids)[0], log=args["logs"])  # type: ignore

    if app.config["TESTING"] == True:
        log.id = 1
    else:
        db.session.add(log)

        # Add users if not present.
        logging.warn("Finding present users.")
        present_users = UserModel.query.filter(
            UserModel.bga_id.in_([user.id for user in parsed_logs.data.players])
        ).all()
        bga_id_to_user = {present.bga_id: present for present in present_users}
        present_user_ids = set(present.bga_id for present in present_users)
        logging.warn(f"Found present users: {present_user_ids}")
        logging.warn(f"Users at this point: {bga_id_to_user}")

        users_to_create = [
            user for user in parsed_logs.data.players if user.id not in present_user_ids
        ]
        logging.warn(f"Users to create: {[u.id for u in users_to_create]}")

        for user in users_to_create:
            bga_id_to_user[user.id] = UserModel(  # type: ignore
                bga_id=user.id,
                name=user.name,
                avatar=user.avatar,
            )
            db.session.add(bga_id_to_user[user.id])

        logging.warn(f"Users at this point: {bga_id_to_user}")

        # Now create a game participation for each user.
        logging.warn("Adding participations.")
        for bga_user in parsed_logs.data.players:
            logging.warn(f"Adding participation for: {bga_user.id}")
            log_user = next(u for u in parsed_logs.data.players if u.id == bga_user.id)
            logging.warn(f"Found log user with color: {log_user.color}")
            logging.warn(f"Users at this point: {bga_id_to_user}")
            db.session.add(
                GameParticipationModel(  # type: ignore
                    user=bga_id_to_user[bga_user.id],
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


def user_fields() -> dict[str, GraphQLField]:
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The id of the user.",
        ),
        "bgaId": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The BGA id of the user.",
        ),
        "name": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The BGA username of the user.",
        ),
        "avatar": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The avatar of the user.",
        ),
    }


user_type = GraphQLObjectType(
    "User",
    description="A game log entry.",
    fields=user_fields,
)
