from graphql import GraphQLObjectType, GraphQLSchema

from ark_nova_stats.api.gql.types.game_log import (
    game_log_field,
    game_logs_field,
    stats_field,
    submit_game_logs_field,
)
from ark_nova_stats.models import GameLog, User


def Schema(app):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="Query",
            fields={
                "gameLog": game_log_field(GameLog),
                "gameLogs": game_logs_field(GameLog),
                "stats": stats_field(GameLog, User),
            },
        ),
        mutation=GraphQLObjectType(
            name="Mutation",
            fields={
                "submitGameLogs": submit_game_logs_field(GameLog),
            },
        ),
    )
