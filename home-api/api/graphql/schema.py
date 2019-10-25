from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLList,
    GraphQLSchema,
    GraphQLString
)
from .types.transaction import transactionsType

def Schema(models):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name='RootQueryType',
            fields={
                'hello': GraphQLField(
                    GraphQLString,
                    resolver=lambda *args: 'world'
                ),
                'transactions': transactionsType(models),
            }
        )
    )