from graphql import GraphQLObjectType, GraphQLSchema

from ark_nova_stats.api.gql.types.game_log import game_log_field, submit_game_logs_field
from ark_nova_stats.models import GameLog


def Schema(app):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="Query",
            fields={
                "gameLog": game_log_field(GameLog),
            },
        ),
        mutation=GraphQLObjectType(
            name="Mutation",
            fields={
                "submitGameLogs": submit_game_logs_field(
                    GameLog
                ),
            },
        ),
    )
