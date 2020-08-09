from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLSchema,
    GraphQLString
)
from .types.transaction import (
    transactionsType,
    amountByMonthType
)

def Schema(models):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name='RootQueryType',
            fields={
                'transactions': transactionsType(models),
                'amountByMonth': amountByMonthType(models),
            }
        )
    )
