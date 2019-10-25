from graphql import (
    GraphQLObjectType,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLSchema,
    GraphQLString
)

transactionTypeEnum = GraphQLEnumType(
    "TransactionType",
    description="Types of transactions",
    values={
        "debit": GraphQLEnumValue('debit', description='A transaction that took money out of an account'),
        "credit": GraphQLEnumValue('credit', description='A transaction that deposited money into an account')
    },
)

transactionType = GraphQLObjectType(
    "Transaction",
    description="A purchase or credit that was made against an account.",
    fields=lambda: {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The id of the transaction."
        ),
        "date": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The time that the transaction was made, in unix epoch time."
            resolver=lambda transaction, info, **args: int(transaction.date.timestamp()),
        ),
        "description": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The cleaned-up description for the transaction."
        ),
        "original_description": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The original description for the transaction, retrieved from the account."
        ),
        "amount": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The amount of the transaction, in cents USD."
        ),
        "type": GraphQLField(
            GraphQLNonNull(transactionTypeEnum),
            description="The type of transaction."
        ),
        "category": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The category of spending / crediting that this transaction falls under."
        ),
        "account": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The account that this transaction was performed within."
        ),
        "labels": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="User-attached labels on the transaction."
        ),
        "notes": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="Notes defined on the transaction."
        ),
    }
)

def schema(models):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name='RootQueryType',
            fields={
                'hello': GraphQLField(
                    GraphQLString,
                    resolver=lambda *args: 'world'
                ),
                'transactions': GraphQLField(
                    GraphQLList(transactionType),
                    resolver=lambda *args: models.Transaction.query.all()
                )
            }
        )
    )