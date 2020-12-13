from graphql import GraphQLObjectType, GraphQLSchema
from .types.server import (
    serversField,
    createServerField,
)
from .types.server_log import (
    serverLogsField,
    createServerLogField,
)


def Schema(models):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="RootQueryType",
            fields={
                "servers": serversField(models),
                "serverLogs": serverLogsField(models),
            },
        ),
        mutation=GraphQLObjectType(
            name="RootMutationType",
            fields={
                "createServer": createServerField(models),
                "createServerLog": createServerLogField(models),
            },
        ),
    )
