from graphql import GraphQLField, GraphQLObjectType, GraphQLSchema, GraphQLString

from home_api.api.graphql.types.transaction import (
    accountsField,
    amountByMonthField,
    amountRangeField,
    categoriesField,
    dateRangeField,
    transactionsField,
    typesField,
)


def Schema():
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="RootQueryType",
            fields={
                "transactions": transactionsField(),
                "amountByMonth": amountByMonthField(),
                "accounts": accountsField(),
                "amountRange": amountRangeField(),
                "categories": categoriesField(),
                "dateRange": dateRangeField(),
                "types": typesField(),
            },
        )
    )
