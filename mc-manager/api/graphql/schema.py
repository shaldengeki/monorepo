from graphql import GraphQLObjectType, GraphQLSchema
from .types.server import (
    serversField,
)


def Schema(models):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="RootQueryType",
            fields={
                "servers": serversField(models),
            },
        )
    )
