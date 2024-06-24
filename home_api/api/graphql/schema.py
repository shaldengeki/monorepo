from graphql import GraphQLField, GraphQLObjectType, GraphQLSchema, GraphQLString

from .types.transaction import (
    accountsField,
    amountByMonthField,
    amountRangeField,
    categoriesField,
    dateRangeField,
    transactionsField,
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
