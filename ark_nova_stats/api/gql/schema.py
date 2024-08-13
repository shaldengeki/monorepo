import flask
from graphql import GraphQLObjectType, GraphQLSchema

from ark_nova_stats.api.gql.types.game_log import (
    fetch_card_field,
    fetch_user_field,
    game_log_field,
    game_logs_field,
    recent_game_log_archives_field,
    recent_game_logs_field,
    stats_field,
    submit_game_logs_field,
)
from ark_nova_stats.models import Card, GameLog, GameLogArchive, User


def Schema(app: flask.Flask):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="Query",
            fields={
                "gameLog": game_log_field(GameLog),
                "gameLogs": game_logs_field(GameLog),
                "recentGameLogs": recent_game_logs_field(GameLog),
                "recentGameLogArchives": recent_game_log_archives_field(GameLogArchive),
                "stats": stats_field(GameLog, User),
                "user": fetch_user_field(User),
                "card": fetch_card_field(Card),
            },
        ),
        mutation=GraphQLObjectType(
            name="Mutation",
            fields={
                "submitGameLogs": submit_game_logs_field(GameLog),
            },
        ),
    )
