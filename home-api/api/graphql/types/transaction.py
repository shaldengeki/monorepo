import collections
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
    GraphQLString,
)
from sqlalchemy import asc, desc, distinct
from sqlalchemy.sql import func

transactionTypeEnum = GraphQLEnumType(
    "TransactionType",
    description="Types of transactions",
    values={
        "debit": GraphQLEnumValue(
            "debit", description="A transaction that took money out of an account"
        ),
        "credit": GraphQLEnumValue(
            "credit", description="A transaction that deposited money into an account"
        ),
    },
)

transactionType = GraphQLObjectType(
    "Transaction",
    description="A purchase or credit that was made against an account.",
    fields=lambda: {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLString), description="The id of the transaction."
        ),
        "date": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the transaction was made, in unix epoch time.",
            resolver=lambda transaction, info, **args: int(
                transaction.date.timestamp()
            ),
        ),
        "formattedDate": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The date that the transaction was made, in YYYY-MM-DD format.",
            resolver=lambda transaction, info, **args: transaction.date.strftime(
                "%Y-%m-%d"
            ),
        ),
        "description": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The cleaned-up description for the transaction.",
        ),
        "originalDescription": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The original description for the transaction, retrieved from the account.",
            resolver=lambda transaction, info, **args: transaction.original_description,
        ),
        "amount": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The amount of the transaction, in cents USD.",
        ),
        "type": GraphQLField(
            GraphQLNonNull(transactionTypeEnum), description="The type of transaction."
        ),
        "category": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The category of spending / crediting that this transaction falls under.",
        ),
        "account": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The account that this transaction was performed within.",
        ),
        "labels": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="User-attached labels on the transaction.",
        ),
        "notes": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="Notes defined on the transaction.",
        ),
    },
)

amountOverTimeType = GraphQLObjectType(
    "AmountOverTime",
    description="A summed-up amount representing transactions grouped over some time bucket.",
    fields=lambda: {
        "date": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The start of the time bucket, in unix epoch time.",
        ),
        "formattedMonth": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The start of the time bucket, YYYY-MM-01 format.",
            resolver=lambda obj, info, **args: datetime.datetime.utcfromtimestamp(
                obj.date
            ).strftime("%Y-%m-01"),
        ),
        "amount": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The summed amount of transactions within the bucket, in cents USD.",
        ),
        "transactions": GraphQLField(
            GraphQLNonNull(GraphQLList(transactionType)),
            description="The transactions that fall within the current bucket",
        ),
    },
)

dateRangeType = GraphQLObjectType(
    "DateRange",
    description="A date range, represented by a start and end date.",
    fields=lambda: {
        "start": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The start of the date range, in unix epoch time.",
        ),
        "end": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The end of the date range, in unix epoch time.",
        ),
    },
)

DateRange = collections.namedtuple("DateRange", ["start", "end"])

amountRangeType = GraphQLObjectType(
    "AmountRange",
    description="An amount range, represented by a minimum and maximum amount.",
    fields=lambda: {
        "min": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The minimum of the amount range, in cents USD.",
        ),
        "max": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The maximum of the amount range, in cents USD.",
        ),
    },
)

AmountRange = collections.namedtuple("AmountRange", ["min", "max"])


def fetch_transactions(models, params):
    query_obj = models.Transaction.query
    if params.get("earliestDate", False):
        query_obj = query_obj.filter(
            models.Transaction.date
            >= datetime.datetime.utcfromtimestamp(int(params["earliestDate"]))
        )
    if params.get("latestDate", False):
        query_obj = query_obj.filter(
            models.Transaction.date
            <= datetime.datetime.utcfromtimestamp(int(params["latestDate"]))
        )
    if params.get("minAmount", False):
        query_obj = query_obj.filter(
            models.Transaction.amount >= int(params["minAmount"])
        )
    if params.get("maxAmount", False):
        query_obj = query_obj.filter(
            models.Transaction.amount <= int(params["maxAmount"])
        )
    if params.get("description", False):
        query_obj = query_obj.filter(
            models.Transaction.description == params["description"]
        )
    if params.get("type", False):
        query_obj = query_obj.filter(models.Transaction.type == params["type"])
    if params.get("category", False):
        query_obj = query_obj.filter(models.Transaction.category == params["category"])
    if params.get("account", False):
        query_obj = query_obj.filter(models.Transaction.account == params["account"])
    return query_obj.order_by(desc(models.Transaction.date)).all()


AggregatedTransaction = collections.namedtuple(
    "AggregatedTransaction", ["date", "amount", "transactions"]
)


def aggregate_transactions(transactions):
    results = []
    for group, items in itertools.groupby(
        transactions, lambda t: t.date.strftime("%Y-%m")
    ):
        results.append(
            AggregatedTransaction(
                date=datetime.datetime.strptime(group, "%Y-%m").timestamp(),
                amount=sum(
                    t.amount if t.type == "debit" else -1 * t.amount for t in items
                ),
                transactions=items,
            )
        )
    return results


transactionsFilters = {
    "earliestDate": GraphQLArgument(
        description="Earliest date that a transaction should have.", type=GraphQLInt
    ),
    "latestDate": GraphQLArgument(
        description="Latest date that a transaction should have.", type=GraphQLInt
    ),
    "minAmount": GraphQLArgument(
        description="Lowest amount that a transaction should have.", type=GraphQLInt
    ),
    "maxAmount": GraphQLArgument(
        description="Highest amount that a transaction should have.", type=GraphQLInt
    ),
    "description": GraphQLArgument(
        description="Value for description that a transaction should have.",
        type=GraphQLString,
    ),
    "type": GraphQLArgument(
        description="Value for type that a transaction should have.", type=GraphQLString
    ),
    "category": GraphQLArgument(
        description="Value for category that a transaction should have.",
        type=GraphQLString,
    ),
    "account": GraphQLArgument(
        description="Value for account that a transaction should have.",
        type=GraphQLString,
    ),
}


def transactionsField(models):
    return GraphQLField(
        GraphQLList(transactionType),
        args=transactionsFilters,
        resolver=lambda root, info, **args: fetch_transactions(models, args),
    )


def amountByMonthField(models):
    return GraphQLField(
        GraphQLList(amountOverTimeType),
        args=transactionsFilters,
        resolver=lambda root, info, **args: aggregate_transactions(
            fetch_transactions(models, args)
        ),
    )


def fetch_transaction_date_range(models):
    dates = models.Transaction.query(
        func.max(models.Transaction.date).label("max_date"),
        func.min(models.Transaction.date).label("min_date"),
    ).one()
    return DateRange(start=dates.min_date, end=dates.max_date)


def fetch_transaction_amount_range(models):
    amounts = models.Transaction.query(
        func.max(models.Transaction.amount).label("max_amount"),
        func.min(models.Transaction.amount).label("min_amount"),
    ).one()
    return AmountRange(min=amounts.min_amount, max=amounts.max_amount)


def dateRangeField(models):
    return GraphQLField(
        dateRangeType,
        resolver=lambda root, info, **args: fetch_transaction_date_range(models),
    )


def amountRangeField(models):
    return GraphQLField(
        amountRangeType,
        resolver=lambda root, info, **args: fetch_transaction_amount_range(models),
    )


def fetch_transaction_categories(models):
    categories = (
        models.Transaction.query(distinct(Transaction.category).label("category"))
        .order_by(asc(models.Transaction.category))
        .all()
    )
    return [t.category for t in categories]


def categoriesField(models):
    return GraphQLField(
        GraphQLList(GraphQLString),
        resolver=lambda root, info, **args: fetch_transaction_categories(models),
    )
