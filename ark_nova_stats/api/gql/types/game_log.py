import json
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
from sqlalchemy import desc

from ark_nova_stats.bga_log_parser.game_log import GameLog as ParsedGameLog
from ark_nova_stats.config import app, db
from ark_nova_stats.models import GameLog as GameLogModel
from ark_nova_stats.models import GameLogArchive as GameLogArchiveModel
from ark_nova_stats.models import GameLogArchiveType
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
        GraphQLNonNull(game_log_type),
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

        for obj in log.create_related_objects(parsed_logs):
            db.session.add(obj)

        db.session.commit()

    return log


def submit_game_logs_field(
    game_log_model: Type[GameLogModel],
) -> GraphQLField:
    return GraphQLField(
        GraphQLNonNull(game_log_type),
        description="Submit logs for a game.",
        args={
            "logs": GraphQLArgument(
                GraphQLNonNull(GraphQLString),
                description="JSON-encoded representation of game logs.",
            ),
        },
        resolve=lambda root, info, **args: submit_game_logs(game_log_model, args),
    )


def fetch_game_logs(game_log_model: Type[GameLogModel]) -> list[GameLogModel]:
    return game_log_model.query.all()


def game_logs_field(
    game_log_model: Type[GameLogModel],
) -> GraphQLField:
    return GraphQLField(
        GraphQLNonNull(GraphQLList(game_log_type)),
        description="List all game logs.",
        args={},
        resolve=lambda root, info, **args: fetch_game_logs(game_log_model),
    )


def fetch_recent_game_logs(game_log_model: Type[GameLogModel]) -> list[GameLogModel]:
    return (
        game_log_model.query.order_by(desc(game_log_model.bga_table_id)).limit(10).all()
    )


def recent_game_logs_field(
    game_log_model: Type[GameLogModel],
) -> GraphQLField:
    return GraphQLField(
        GraphQLNonNull(GraphQLList(game_log_type)),
        description="List recent game logs.",
        args={},
        resolve=lambda root, info, **args: fetch_recent_game_logs(game_log_model),
    )


def user_bga_id_resolver(user: UserModel, info, **args) -> int:
    return user.bga_id


def user_game_logs_resolver(user: UserModel, info, **args) -> list[GameLogModel]:
    return user.game_logs


def user_num_game_logs_resolver(user: UserModel, info, **args) -> int:
    return len(user.game_logs)


def user_fields() -> dict[str, GraphQLField]:
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The id of the user.",
        ),
        "bgaId": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The BGA id of the user.",
            resolve=user_bga_id_resolver,
        ),
        "name": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The BGA username of the user.",
        ),
        "avatar": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The avatar of the user.",
        ),
        "gameLogs": GraphQLField(
            GraphQLNonNull(GraphQLList(game_log_type)),
            description="This user's game logs.",
            resolve=user_game_logs_resolver,
        ),
        "numGameLogs": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="Number of game logs for this user.",
            resolve=user_num_game_logs_resolver,
        ),
    }


user_type = GraphQLObjectType(
    "User",
    description="A game log entry.",
    fields=user_fields,
)

fetch_user_filters: dict[str, GraphQLArgument] = {
    "name": GraphQLArgument(
        GraphQLNonNull(GraphQLString),
        description="BGA username of the user.",
    ),
}


def fetch_user(
    user_model: Type[UserModel],
    params: dict[str, Any],
) -> Optional[UserModel]:
    return user_model.query.where(user_model.name == params["name"]).first()


def fetch_user_field(
    user_model: Type[UserModel],
) -> GraphQLField:
    return GraphQLField(
        GraphQLNonNull(user_type),
        description="Fetch information about a single user.",
        args=fetch_user_filters,
        resolve=lambda root, info, **args: fetch_user(user_model, args),
    )


def stats_fields() -> dict[str, GraphQLField]:
    return {
        "numGameLogs": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="Number of game logs in the database.",
        ),
        "numPlayers": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="Number of players in the database.",
        ),
        "mostRecentSubmission": GraphQLField(
            GraphQLInt,
            description="UNIX timestamp for the most recently-submitted game in the database.",
        ),
    }


stats_type = GraphQLObjectType(
    "Stats",
    description="A game log entry.",
    fields=stats_fields,
)


def fetch_stats(
    game_log_model: Type[GameLogModel], user_model: Type[UserModel]
) -> dict:
    most_recent_submission = game_log_model.query.order_by(
        desc(game_log_model.created_at)
    ).first()
    if most_recent_submission is None:
        most_recent_time = None
    else:
        most_recent_time = int(most_recent_submission.created_at.timestamp())

    return {
        "numGameLogs": game_log_model.query.count(),
        "numPlayers": user_model.query.count(),
        "mostRecentSubmission": most_recent_time,
    }


def stats_field(
    game_log_model: Type[GameLogModel],
    user_model: Type[UserModel],
) -> GraphQLField:
    return GraphQLField(
        GraphQLNonNull(stats_type),
        description="Fetch database statistics.",
        args={},
        resolve=lambda root, info, **args: fetch_stats(game_log_model, user_model),
    )


def game_log_archive_archive_type_resolver(
    game_log_archive: GameLogArchiveModel, info, **args
) -> str:
    return GameLogArchiveType(game_log_archive.archive_type).name


def game_log_archive_size_bytes_resolver(
    game_log_archive: GameLogArchiveModel, info, **args
) -> int:
    return game_log_archive.size_bytes


def game_log_archive_num_game_logs_resolver(
    game_log_archive: GameLogArchiveModel, info, **args
) -> int:
    return game_log_archive.num_game_logs


def game_log_archive_num_users_resolver(
    game_log_archive: GameLogArchiveModel, info, **args
) -> int:
    return game_log_archive.num_users


def game_log_archive_max_game_log_resolver(
    game_log_archive: GameLogArchiveModel, info, **args
) -> Optional[GameLogModel]:
    return game_log_archive.last_game_log


def game_log_archive_created_at_resolver(
    game_log_archive: GameLogArchiveModel, info, **args
) -> int:
    return int(round(game_log_archive.created_at.timestamp()))


def game_log_archive_fields() -> dict[str, GraphQLField]:
    archive_types = set(t.name for t in GameLogArchiveType)
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="ID of game log archive.",
        ),
        "archiveType": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description=f"Type of game logs. Possible values are: {', '.join(archive_types)}.",
            resolve=game_log_archive_archive_type_resolver,
        ),
        "url": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description=f"URL of archive.",
        ),
        "sizeBytes": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description=f"Size of archive, in bytes.",
            resolve=game_log_archive_size_bytes_resolver,
        ),
        "numGameLogs": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description=f"Number of game logs in this archive.",
            resolve=game_log_archive_num_game_logs_resolver,
        ),
        "numUsers": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description=f"Number of users in this archive.",
            resolve=game_log_archive_num_users_resolver,
        ),
        "maxGameLog": GraphQLField(
            game_log_type,
            description=f"The game log with the highest BGA table ID.",
            resolve=game_log_archive_max_game_log_resolver,
        ),
        "createdAt": GraphQLField(
            GraphQLInt,
            description="UNIX timestamp for when this archive was created.",
            resolve=game_log_archive_created_at_resolver,
        ),
    }


game_log_archive_type = GraphQLObjectType(
    "GameLogArchive",
    description="An archive of game logs.",
    fields=game_log_archive_fields,
)


def fetch_recent_game_log_archives(
    game_log_archive_model: Type[GameLogArchiveModel],
) -> list[GameLogArchiveModel]:
    return (
        game_log_archive_model.query.order_by(desc(game_log_archive_model.created_at))
        .limit(10)
        .all()
    )


def recent_game_log_archives_field(
    game_log_archive_model: Type[GameLogArchiveModel],
) -> GraphQLField:
    return GraphQLField(
        GraphQLNonNull(GraphQLList(game_log_archive_type)),
        description="List recent game log archives.",
        args={},
        resolve=lambda root, info, **args: fetch_recent_game_log_archives(
            game_log_archive_model
        ),
    )
