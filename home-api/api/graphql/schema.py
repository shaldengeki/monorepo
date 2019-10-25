from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLSchema,
    GraphQLString
)
from .types.transaction import transactionsType

def Schema(models):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name='RootQueryType',
            fields={
                'transactions': transactionsType(models),
            }
        )
    )