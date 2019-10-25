import datetime
import itertools
from graphql import (
    GraphQLArgument,
    GraphQLObjectType,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
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
            description="The time that the transaction was made, in unix epoch time.",
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

amountOverTimeType = GraphQLObjectType(
    "AmountOverTime",
    description="A summed-up amount representing transactions grouped over some time bucket.",
    fields=lambda: {
        "date": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The start of the time bucket, in unix epoch time.",
            resolver=lambda transaction, info, **args: int(transaction.date.timestamp()),
        ),
        "amount": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The summed amount of transactions within the bucket, in cents USD."
        ),
        "transactions": GraphQLField(
            GraphQLNonNull(GraphQLList(transactionType)),
            description="The transactions that fall within the current bucket"
        )
    }
)

def fetch_transactions(models, params):
    query_obj = models.Transaction.query
    if params.get('earliestDate', False):
        query_obj = query_obj.filter(models.Transaction.date >= datetime.datetime.utcfromtimestamp(int(params['earliestDate'])))
    if params.get('latestDate', False):
        query_obj = query_obj.filter(models.Transaction.date <= datetime.datetime.utcfromtimestamp(int(params['latestDate'])))
    if params.get('minAmount', False):
        query_obj = query_obj.filter(models.Transaction.amount >= int(params['minAmount']))
    if params.get('maxAmount', False):
        query_obj = query_obj.filter(models.Transaction.amount <= int(params['maxAmount']))
    if params.get('description', False):
        query_obj = query_obj.filter(models.Transaction.description == params['description'])
    if params.get('type', False):
        query_obj = query_obj.filter(models.Transaction.type == params['type'])
    if params.get('category', False):
        query_obj = query_obj.filter(models.Transaction.category == params['category'])
    if params.get('account', False):
        query_obj = query_obj.filter(models.Transaction.account == params['account'])
    return query_obj.all()

def aggregate_transactions(transactions):
    results = []
    for group, items in itertools.groupby(transactions, lambda t: t.date.strftime('%Y-%m')):
        results.append({
            'date': datetime.datetime.strptime(group, '%Y-%m').timestamp(),
            'amount': sum(t.amount for t in items),
            'transactions': items,
        })
    return results

transactionsFilters = {
    "earliestDate": GraphQLArgument(
        description="Earliest date that a transaction should have.",
        type=GraphQLInt
    ),
    "latestDate": GraphQLArgument(
        description="Latest date that a transaction should have.",
        type=GraphQLInt
    ),
    "minAmount": GraphQLArgument(
        description="Lowest amount that a transaction should have.",
        type=GraphQLInt
    ),
    "maxAmount": GraphQLArgument(
        description="Highest amount that a transaction should have.",
        type=GraphQLInt
    ),
    "description": GraphQLArgument(
        description="Value for description that a transaction should have.",
        type=GraphQLString
    ),
    "type": GraphQLArgument(
        description="Value for type that a transaction should have.",
        type=GraphQLString
    ),
    "category": GraphQLArgument(
        description="Value for category that a transaction should have.",
        type=GraphQLString
    ),
    "account": GraphQLArgument(
        description="Value for account that a transaction should have.",
        type=GraphQLString
    ),
}

def transactionsType(models):
    return GraphQLField(
        GraphQLList(transactionType),
        args=transactionsFilters,
        resolver=lambda root, info, **args: fetch_transactions(models, args)
    )

def amountByMonthType(models):
    return GraphQLField(
        GraphQLList(amountOverTimeType),
        args=transactionsFilters,
        resolver=lambda root, info, **args: aggregate_transactions(fetch_transactions(models, args))
    )
