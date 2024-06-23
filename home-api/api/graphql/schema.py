from graphql import GraphQLObjectType, GraphQLField, GraphQLSchema, GraphQLString
from .types.transaction import (
    transactionsField,
    amountByMonthField,
    accountsField,
    amountRangeField,
    categoriesField,
    dateRangeField,
    typesField,
)


def Schema(models):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="RootQueryType",
            fields={
                "transactions": transactionsField(models),
                "amountByMonth": amountByMonthField(models),
                "accounts": accountsField(models),
                "amountRange": amountRangeField(models),
                "categories": categoriesField(models),
                "dateRange": dateRangeField(models),
                "types": typesField(models),
            },
        )
    )
