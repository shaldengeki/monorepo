from graphql import GraphQLObjectType, GraphQLSchema
from .types.server import (
    serversField,
)
from .types.server_log import (
    serverLogsField,
)


def Schema(models):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="RootQueryType",
            fields={
                "servers": serversField(models),
                "serverLogs": serverLogsField(models),
            },
        )
    )
