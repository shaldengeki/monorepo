import json
from typing import Any, Optional, Sequence, Type

from graphql import (
    GraphQLArgument,
    GraphQLBoolean,
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
from ark_nova_stats.models import GameStatistics as GameStatisticsModel
from ark_nova_stats.models import User as UserModel


def player_rating_change_fields() -> dict[str, GraphQLField]:
    return {
        "user": GraphQLField(
            GraphQLNonNull(user_type),
            description="The user whose ratings may have changed.",
        ),
        "priorElo": GraphQLField(
            GraphQLInt,
            description="User's non-arena ELO prior to the game.",
        ),
        "newElo": GraphQLField(
            GraphQLInt,
            description="User's non-arena ELO after the game.",
        ),
        "priorArenaElo": GraphQLField(
            GraphQLInt,
            description="User's arena ELO prior to the game.",
        ),
        "newArenaElo": GraphQLField(
            GraphQLInt,
            description="User's arena ELO after the game.",
        ),
    }


player_rating_change_type = GraphQLObjectType(
    "PlayerGameRating",
    description="A struct containing information about how a player's game rating(s) changed after a game.",
    fields=player_rating_change_fields,
)


def game_log_bga_table_id_resolver(game_log: GameLogModel, info, **args) -> int:
    return game_log.bga_table_id


def game_log_start_resolver(game_log: GameLogModel, info, **args) -> int:
    return round(game_log.game_start.timestamp())


def game_log_end_resolver(game_log: GameLogModel, info, **args) -> int:
    return round(game_log.game_end.timestamp())


def game_log_player_rating_changes_resolver(
    game_log: GameLogModel, info, **args
) -> list:
    return [
        {
            "user": rating.user,
            "priorElo": rating.prior_elo,
            "newElo": rating.new_elo,
            "priorArenaElo": rating.prior_arena_elo,
            "newArenaElo": rating.new_arena_elo,
        }
        for rating in game_log.game_ratings
    ]


def game_log_statistics_resolver(
    game_log: GameLogModel, info, **args
) -> list[GameStatisticsModel]:
    return game_log.game_statistics


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
            description="Users who played in this game.",
        ),
        "cards": GraphQLField(
            GraphQLNonNull(GraphQLList(card_type)),
            description="Cards played in this game.",
        ),
        "start": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="UNIX timestamp when the game started.",
            resolve=game_log_start_resolver,
        ),
        "end": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="UNIX timestamp when the game ended.",
            resolve=game_log_end_resolver,
        ),
        "gameRatingChanges": GraphQLField(
            GraphQLNonNull(GraphQLList(player_rating_change_type)),
            description="How players' ratings changed after the game.",
            resolve=game_log_player_rating_changes_resolver,
        ),
        "statistics": GraphQLField(
            GraphQLNonNull(GraphQLList(game_statistics_type)),
            description="End-game statistics for this game.",
            resolve=game_log_statistics_resolver,
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
        bga_table_id=list(table_ids)[0],
        log=args["logs"],
        game_start=parsed_logs.game_start,
        game_end=parsed_logs.game_end,
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


def fetch_game_logs(
    game_log_model: Type[GameLogModel], args: dict
) -> list[GameLogModel]:
    query = game_log_model.query
    if "bgaTableIds" in args:
        query = query.where(game_log_model.bga_table_id.in_(args["bgaTableIds"]))

    return query.limit(500).all()


fetch_game_logs_filters: dict[str, GraphQLArgument] = {
    "bgaTableIds": GraphQLArgument(
        GraphQLList(GraphQLInt),
        description="List of BGA table IDs to fetch.",
    ),
}


def game_logs_field(
    game_log_model: Type[GameLogModel],
) -> GraphQLField:
    return GraphQLField(
        GraphQLNonNull(GraphQLList(game_log_type)),
        description="List all game logs.",
        args=fetch_game_logs_filters,
        resolve=lambda root, info, **args: fetch_game_logs(game_log_model, args),
    )


def fetch_recent_game_logs(game_log_model: Type[GameLogModel]) -> list[GameLogModel]:
    return game_log_model.query.order_by(desc(game_log_model.game_end)).limit(10).all()


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


def user_current_elo_resolver(user: UserModel, info, **args) -> Optional[int]:
    return user.current_elo()


def user_current_arena_elo_resolver(user: UserModel, info, **args) -> Optional[int]:
    return user.current_arena_elo()


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
        "currentElo": GraphQLField(
            GraphQLInt,
            description="Current non-arena ELO.",
            resolve=user_current_elo_resolver,
        ),
        "currentArenaElo": GraphQLField(
            GraphQLInt,
            description="Current non-arena ELO.",
            resolve=user_current_arena_elo_resolver,
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
    limit = min(10, int(args["limit"]))

    return [
        {"user": user, "card": card, "count": count}
        for user, count in db.session.execute(card.most_played_by(num=limit)).all()
    ]


def card_created_at_resolver(card: CardModel, info, **args) -> int:
    return int(round(card.created_at.timestamp()))


most_played_by_filters: dict[str, GraphQLArgument] = {
    "limit": GraphQLArgument(
        GraphQLInt,
        default_value=10,
        description="How many users to return. Maximum of 10 (also the default).",
    ),
}


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
            args=most_played_by_filters,
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


def game_statistics_game_log_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> GameLogModel:
    return game_statistics.game_log


def game_statistics_bga_table_id_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.bga_table_id


def game_statistics_bga_user_id_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.bga_user_id


def game_statistics_created_at_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.created_at


def game_statistics_thinking_time_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.thinking_time


def game_statistics_starting_position_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.starting_position


def game_statistics_breaks_triggered_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.breaks_triggered


def game_statistics_triggered_end_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> bool:
    return game_statistics.triggered_end


def game_statistics_map_id_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.map_id


def game_statistics_actions_build_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.actions_build


def game_statistics_actions_animals_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.actions_animals


def game_statistics_actions_cards_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.actions_cards


def game_statistics_actions_association_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.actions_association


def game_statistics_actions_sponsors_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.actions_sponsors


def game_statistics_x_tokens_gained_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.x_tokens_gained


def game_statistics_x_actions_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.x_actions


def game_statistics_x_tokens_used_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.x_tokens_used


def game_statistics_money_gained_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.money_gained


def game_statistics_money_gained_through_income_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.money_gained_through_income


def game_statistics_money_spent_on_animals_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.money_spent_on_animals


def game_statistics_money_spent_on_enclosures_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.money_spent_on_enclosures


def game_statistics_money_spent_on_donations_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.money_spent_on_donations


def game_statistics_money_spent_on_playing_cards_from_reputation_range_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.money_spent_on_playing_cards_from_reputation_range


def game_statistics_cards_drawn_from_deck_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.cards_drawn_from_deck


def game_statistics_cards_drawn_from_reputation_range_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.cards_drawn_from_reputation_range


def game_statistics_cards_snapped_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.cards_snapped


def game_statistics_cards_discarded_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.cards_discarded


def game_statistics_played_sponsors_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.played_sponsors


def game_statistics_played_animals_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.played_animals


def game_statistics_released_animals_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.released_animals


def game_statistics_association_workers_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.association_workers


def game_statistics_association_donations_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.association_donations


def game_statistics_association_reputation_actions_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.association_reputation_actions


def game_statistics_association_partner_zoo_actions_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.association_partner_zoo_actions


def game_statistics_association_university_actions_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.association_university_actions


def game_statistics_association_conservation_project_actions_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.association_conservation_project_actions


def game_statistics_built_enclosures_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.built_enclosures


def game_statistics_built_kiosks_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.built_kiosks


def game_statistics_built_pavilions_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.built_pavilions


def game_statistics_built_unique_buildings_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.built_unique_buildings


def game_statistics_hexes_covered_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.hexes_covered


def game_statistics_hexes_empty_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.hexes_empty


def game_statistics_upgraded_action_cards_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> bool:
    return game_statistics.upgraded_action_cards


def game_statistics_upgraded_animals_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> bool:
    return game_statistics.upgraded_animals


def game_statistics_upgraded_build_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> bool:
    return game_statistics.upgraded_build


def game_statistics_upgraded_cards_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> bool:
    return game_statistics.upgraded_cards


def game_statistics_upgraded_sponsors_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> bool:
    return game_statistics.upgraded_sponsors


def game_statistics_upgraded_association_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> bool:
    return game_statistics.upgraded_association


def game_statistics_icons_africa_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_africa


def game_statistics_icons_europe_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_europe


def game_statistics_icons_asia_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_asia


def game_statistics_icons_australia_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_australia


def game_statistics_icons_americas_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_americas


def game_statistics_icons_bird_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_bird


def game_statistics_icons_predator_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_predator


def game_statistics_icons_herbivore_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_herbivore


def game_statistics_icons_bear_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_bear


def game_statistics_icons_reptile_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_reptile


def game_statistics_icons_primate_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_primate


def game_statistics_icons_petting_zoo_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_petting_zoo


def game_statistics_icons_sea_animal_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_sea_animal


def game_statistics_icons_water_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_water


def game_statistics_icons_rock_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_rock


def game_statistics_icons_science_resolver(
    game_statistics: GameStatisticsModel, info, **args
) -> int:
    return game_statistics.icons_science


def game_statistics_fields() -> dict[str, GraphQLField]:
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="Unique ID of this set of game statistics",
        ),
        "gameLog": GraphQLField(
            GraphQLNonNull(game_log_type),
            description="Game log that this rating change corresponds to.",
            resolve=game_statistics_game_log_resolver,
        ),
        "user": GraphQLField(
            GraphQLNonNull(user_type),
            description="User that this rating change corresponds to.",
        ),
        "bgaTableId": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The BGA table ID for this game log and user.",
            resolve=game_statistics_bga_table_id_resolver,
        ),
        "bgaUserId": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The BGA user id for this game log and user.",
            resolve=game_statistics_bga_user_id_resolver,
        ),
        "createdAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="When the statistics for this game log and user were recorded.",
            resolve=game_statistics_created_at_resolver,
        ),
        "score": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="Player's score.",
        ),
        "rank": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="Player's final rank. The winner has rank 1.",
        ),
        "thinkingTime": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The thinking time, in seconds, for this game log and user.",
            resolve=game_statistics_thinking_time_resolver,
        ),
        "startingPosition": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The starting position for this game log and user.",
            resolve=game_statistics_starting_position_resolver,
        ),
        "breaksTriggered": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of breaks triggered by this user in this game.",
            resolve=game_statistics_breaks_triggered_resolver,
        ),
        "triggeredEnd": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the user in this game triggered the end of the game.",
            resolve=game_statistics_triggered_end_resolver,
        ),
        "mapId": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The map ID for this game log and user.",
            resolve=game_statistics_map_id_resolver,
        ),
        "actionsBuild": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of build actions for this game log and user.",
            resolve=game_statistics_actions_build_resolver,
        ),
        "actionsAnimals": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of animals actions for this game log and user.",
            resolve=game_statistics_actions_animals_resolver,
        ),
        "actionsCards": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of cards actions for this game log and user.",
            resolve=game_statistics_actions_cards_resolver,
        ),
        "actionsAssociation": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of association actions for this game log and user.",
            resolve=game_statistics_actions_association_resolver,
        ),
        "actionsSponsors": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of sponsors actions for this game log and user.",
            resolve=game_statistics_actions_sponsors_resolver,
        ),
        "xTokensGained": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of X tokens gained for this game log and user.",
            resolve=game_statistics_x_tokens_gained_resolver,
        ),
        "xActions": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of X actions taken for this game log and user.",
            resolve=game_statistics_x_actions_resolver,
        ),
        "xTokensUsed": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of X tokens used for this game log and user.",
            resolve=game_statistics_x_tokens_used_resolver,
        ),
        "moneyGained": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The money gained for this game log and user.",
            resolve=game_statistics_money_gained_resolver,
        ),
        "moneyGainedThroughIncome": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The money gained through income for this game log and user.",
            resolve=game_statistics_money_gained_through_income_resolver,
        ),
        "moneySpentOnAnimals": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The money spent on animals for this game log and user.",
            resolve=game_statistics_money_spent_on_animals_resolver,
        ),
        "moneySpentOnEnclosures": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The money spent on enclosures for this game log and user.",
            resolve=game_statistics_money_spent_on_enclosures_resolver,
        ),
        "moneySpentOnDonations": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The money spent on donations for this game log and user.",
            resolve=game_statistics_money_spent_on_donations_resolver,
        ),
        "moneySpentOnPlayingCardsFromReputationRange": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The money spent on playing cards from reputation range for this game log and user.",
            resolve=game_statistics_money_spent_on_playing_cards_from_reputation_range_resolver,
        ),
        "cardsDrawnFromDeck": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of cards drawn from deck for this game log and user.",
            resolve=game_statistics_cards_drawn_from_deck_resolver,
        ),
        "cardsDrawnFromReputationRange": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of cards drawn from reputation range for this game log and user.",
            resolve=game_statistics_cards_drawn_from_reputation_range_resolver,
        ),
        "cardsSnapped": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of cards snapped for this game log and user.",
            resolve=game_statistics_cards_snapped_resolver,
        ),
        "cardsDiscarded": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of cards discarded for this game log and user.",
            resolve=game_statistics_cards_discarded_resolver,
        ),
        "playedSponsors": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of played sponsors for this game log and user.",
            resolve=game_statistics_played_sponsors_resolver,
        ),
        "playedAnimals": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of played animals for this game log and user.",
            resolve=game_statistics_played_animals_resolver,
        ),
        "releasedAnimals": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of released animals for this game log and user.",
            resolve=game_statistics_released_animals_resolver,
        ),
        "associationWorkers": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of association workers for this game log and user.",
            resolve=game_statistics_association_workers_resolver,
        ),
        "associationDonations": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of association donations for this game log and user.",
            resolve=game_statistics_association_donations_resolver,
        ),
        "associationReputationActions": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of association reputation actions for this game log and user.",
            resolve=game_statistics_association_reputation_actions_resolver,
        ),
        "associationPartnerZooActions": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of association partner zoo actions for this game log and user.",
            resolve=game_statistics_association_partner_zoo_actions_resolver,
        ),
        "associationUniversityActions": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of association university actions for this game log and user.",
            resolve=game_statistics_association_university_actions_resolver,
        ),
        "associationConservationProjectActions": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of association conservation project actions for this game log and user.",
            resolve=game_statistics_association_conservation_project_actions_resolver,
        ),
        "builtEnclosures": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of built enclosures for this game log and user.",
            resolve=game_statistics_built_enclosures_resolver,
        ),
        "builtKiosks": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of built kiosks for this game log and user.",
            resolve=game_statistics_built_kiosks_resolver,
        ),
        "builtPavilions": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of built pavilions for this game log and user.",
            resolve=game_statistics_built_pavilions_resolver,
        ),
        "builtUnique_buildings": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of built unique buildings for this game log and user.",
            resolve=game_statistics_built_unique_buildings_resolver,
        ),
        "hexesCovered": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of covered map hexes for this game log and user.",
            resolve=game_statistics_hexes_covered_resolver,
        ),
        "hexesEmpty": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of empty max hexes for this game log and user.",
            resolve=game_statistics_hexes_empty_resolver,
        ),
        "upgradedActionCards": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of upgraded action cards for this game log and user.",
            resolve=game_statistics_upgraded_action_cards_resolver,
        ),
        "upgradedAnimals": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the user upgraded animals in this game.",
            resolve=game_statistics_upgraded_animals_resolver,
        ),
        "upgradedBuild": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the user upgraded build in this game.",
            resolve=game_statistics_upgraded_build_resolver,
        ),
        "upgradedCards": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the user upgraded cards in this game.",
            resolve=game_statistics_upgraded_cards_resolver,
        ),
        "upgradedSponsors": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the user upgraded sponsors in this game.",
            resolve=game_statistics_upgraded_sponsors_resolver,
        ),
        "upgradedAssociation": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the user upgraded association in this game.",
            resolve=game_statistics_upgraded_association_resolver,
        ),
        "iconsAfrica": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of africa icons for this game log and user.",
            resolve=game_statistics_icons_africa_resolver,
        ),
        "iconsEurope": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of europe icons for this game log and user.",
            resolve=game_statistics_icons_europe_resolver,
        ),
        "iconsAsia": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of asia icons for this game log and user.",
            resolve=game_statistics_icons_asia_resolver,
        ),
        "iconsAustralia": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of australia icons for this game log and user.",
            resolve=game_statistics_icons_australia_resolver,
        ),
        "iconsAmericas": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of americas icons for this game log and user.",
            resolve=game_statistics_icons_americas_resolver,
        ),
        "iconsBird": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of bird icons for this game log and user.",
            resolve=game_statistics_icons_bird_resolver,
        ),
        "iconsPredator": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of predator icons for this game log and user.",
            resolve=game_statistics_icons_predator_resolver,
        ),
        "iconsHerbivore": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of herbivore icons for this game log and user.",
            resolve=game_statistics_icons_herbivore_resolver,
        ),
        "iconsBear": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of bear icons for this game log and user.",
            resolve=game_statistics_icons_bear_resolver,
        ),
        "iconsReptile": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of reptile icons for this game log and user.",
            resolve=game_statistics_icons_reptile_resolver,
        ),
        "iconsPrimate": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of primate icons for this game log and user.",
            resolve=game_statistics_icons_primate_resolver,
        ),
        "iconsPetting_zoo": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of petting_zoo icons for this game log and user.",
            resolve=game_statistics_icons_petting_zoo_resolver,
        ),
        "iconsSea_animal": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of sea_animal icons for this game log and user.",
            resolve=game_statistics_icons_sea_animal_resolver,
        ),
        "iconsWater": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of water icons for this game log and user.",
            resolve=game_statistics_icons_water_resolver,
        ),
        "iconsRock": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of rock icons for this game log and user.",
            resolve=game_statistics_icons_rock_resolver,
        ),
        "iconsScience": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of science icons for this game log and user.",
            resolve=game_statistics_icons_science_resolver,
        ),
    }


game_statistics_type = GraphQLObjectType(
    "GameStatistics",
    description="End-game statistics for a game.",
    fields=game_statistics_fields,
)
