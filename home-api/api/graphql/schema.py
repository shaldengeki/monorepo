from graphql import GraphQLObjectType, GraphQLField, GraphQLSchema, GraphQLString
from .types.transaction import transactionsField, amountByMonthField, dateRangeField


def Schema(models):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="RootQueryType",
            fields={
                "transactions": transactionsField(models),
                "amountByMonth": amountByMonthField(models),
                "dateRange": dateRangeField(models),
            },
        )
    )
