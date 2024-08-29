import json
from typing import Any, Optional, Sequence, Type

from graphql import (
    GraphQLArgument,
    GraphQLField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLString,
)
from sqlalchemy import asc, desc

from ark_nova_stats.bga_log_parser.game_log import GameLog as ParsedGameLog
from ark_nova_stats.config import app, db
from ark_nova_stats.models import Card as CardModel
from ark_nova_stats.models import GameLog as GameLogModel
from ark_nova_stats.models import GameLogArchive as GameLogArchiveModel
from ark_nova_stats.models import GameLogArchiveType
from ark_nova_stats.models import User as UserModel


def game_log_bga_table_id_resolver(game_log: GameLogModel, info, **args) -> int:
    return game_log.bga_table_id


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
        ),
        "cards": GraphQLField(
            GraphQLNonNull(GraphQLList(card_type)),
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

    log: GameLogModel = game_log_model(
        bga_table_id=list(table_ids)[0], log=args["logs"]
    )
    if app.config["TESTING"] == True:
        log.id = 1
    else:
        # Only create the log if it doesn't already exist.
        existing_log: GameLogModel | None = game_log_model.query.filter(
            game_log_model.bga_table_id == log.bga_table_id
        ).first()
        if existing_log is None:
            db.session.add(log)
        else:
            log = existing_log

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


def user_recent_game_logs_resolver(user: UserModel, info, **args) -> list[GameLogModel]:
    return user.recent_game_logs


def user_num_game_logs_resolver(user: UserModel, info, **args) -> int:
    return user.num_game_logs


def user_play_count_fields() -> dict[str, GraphQLField]:
    return {
        "user": GraphQLField(
            GraphQLNonNull(user_type),
            description="The user playing the card.",
        ),
        "card": GraphQLField(
            GraphQLNonNull(card_type),
            description="The card played by the user.",
        ),
        "count": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of times played by the user.",
        ),
    }


user_play_count_type = GraphQLObjectType(
    "UserPlayCount",
    description="The number of times a user played a card.",
    fields=user_play_count_fields,
)


def user_commonly_played_cards_resolver(user: UserModel, info, **args) -> list[dict]:
    return [
        {"user": user, "card": card, "count": count}
        for card, count in db.session.execute(user.commonly_played_cards()).all()
    ]


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
        "recentGameLogs": GraphQLField(
            GraphQLNonNull(GraphQLList(game_log_type)),
            description="This user's recent game logs.",
            resolve=user_recent_game_logs_resolver,
        ),
        "numGameLogs": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="Number of game logs for this user.",
            resolve=user_num_game_logs_resolver,
        ),
        "commonlyPlayedCards": GraphQLField(
            GraphQLNonNull(GraphQLList(user_play_count_type)),
            description="Most commonly played cards by the user.",
            resolve=user_commonly_played_cards_resolver,
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
        user_type,
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


def card_bga_id_resolver(card: CardModel, info, **args) -> str:
    return card.bga_id


def card_recent_game_logs_resolver(
    card: CardModel, info, **args
) -> Sequence[GameLogModel]:
    return db.session.scalars(card.recent_game_logs()).all()


def card_recent_users_resolver(card: CardModel, info, **args) -> Sequence[UserModel]:
    return db.session.scalars(card.recent_users()).all()


def card_most_played_by_resolver(card: CardModel, info, **args) -> list[dict]:
    return [
        {"user": user, "card": card, "count": count}
        for user, count in db.session.execute(card.most_played_by()).all()
    ]


def card_created_at_resolver(card: CardModel, info, **args) -> int:
    return int(round(card.created_at.timestamp()))


def card_fields() -> dict[str, GraphQLField]:
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="ID of card.",
        ),
        "name": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="Name of card.",
        ),
        "bgaId": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="Card ID on BGA.",
            resolve=card_bga_id_resolver,
        ),
        "recentGameLogs": GraphQLField(
            GraphQLNonNull(GraphQLList(game_log_type)),
            description="Recent game logs where this card was played.",
            resolve=card_recent_game_logs_resolver,
        ),
        "recentUsers": GraphQLField(
            GraphQLNonNull(GraphQLList(user_type)),
            description="Players who played this in a recent game.",
            resolve=card_recent_game_logs_resolver,
        ),
        "mostPlayedBy": GraphQLField(
            GraphQLNonNull(GraphQLList(user_play_count_type)),
            description="Players who play this card most often.",
            resolve=card_most_played_by_resolver,
        ),
        "createdAt": GraphQLField(
            GraphQLInt,
            description="UNIX timestamp for when this archive was created.",
            resolve=card_created_at_resolver,
        ),
    }


card_type = GraphQLObjectType(
    "Card",
    description="An archive of game logs.",
    fields=card_fields,
)


def fetch_card(
    card_model: Type[CardModel],
    params: dict[str, Any],
) -> Optional[CardModel]:
    return card_model.query.where(card_model.bga_id == params["id"]).first()


fetch_card_filters: dict[str, GraphQLArgument] = {
    "id": GraphQLArgument(
        GraphQLNonNull(GraphQLString),
        description="BGA ID of the card.",
    ),
}


def fetch_card_field(
    card_model: Type[CardModel],
) -> GraphQLField:
    return GraphQLField(
        card_type,
        description="Fetch information about a single card.",
        args=fetch_card_filters,
        resolve=lambda root, info, **args: fetch_card(card_model, args),
    )


def fetch_cards(card_model: Type[CardModel]) -> list[CardModel]:
    return card_model.query.order_by(asc(card_model.name)).all()


def fetch_cards_field(
    card_model: Type[CardModel],
) -> GraphQLField:
    return GraphQLField(
        GraphQLNonNull(GraphQLList(card_type)),
        description="List cards.",
        args={},
        resolve=lambda root, info, **args: fetch_cards(card_model),
    )
