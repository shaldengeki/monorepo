import datetime
from graphql import (
    GraphQLArgument,
    GraphQLObjectType,
    GraphQLField,
    GraphQLBoolean,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLString,
)
from sqlalchemy import desc

serverLogType = GraphQLObjectType(
    "ServerLog",
    description="The state of a Server, recorded at a point in time.",
    fields=lambda: {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt), description="The id of the log."
        ),
        "server_id": GraphQLField(
            GraphQLNonNull(GraphQLInt), description="The id of the server."
        ),
        "created": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the log was recorded, in unix epoch time.",
            resolver=lambda transaction, info, **args: int(
                transaction.created.timestamp()
            ),
        ),
        "state": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The recorded state of the server.",
        ),
        "error": GraphQLField(
            GraphQLString, description="The error (if any) encountered by the server."
        ),
    },
)


def fetch_server_logs(models, params):
    query_obj = models.ServerLog.query
    if params.get("earliestDate", False):
        query_obj = query_obj.filter(
            models.ServerLog.created
            >= datetime.datetime.utcfromtimestamp(int(params["earliestDate"]))
        )
    if params.get("latestDate", False):
        query_obj = query_obj.filter(
            models.ServerLog.created
            <= datetime.datetime.utcfromtimestamp(int(params["latestDate"]))
        )
    if params.get("serverId", False):
        query_obj = query_obj.filter(models.ServerLog.server_id == params["serverId"])
    if params.get("state", False):
        query_obj = query_obj.filter(models.ServerLog.state == params["state"])
    if params.get("error", False):
        query_obj = query_obj.filter(models.ServerLog.error != None)

    return query_obj.order_by(desc(models.ServerLog.created)).all()


serverLogsFilters = {
    "earliestDate": GraphQLArgument(
        description="Earliest creation date that a server should have.", type=GraphQLInt
    ),
    "latestDate": GraphQLArgument(
        description="Latest creation date that a server should have.", type=GraphQLInt
    ),
    "serverId": GraphQLArgument(
        description="ID of the server.",
        type=GraphQLString,
    ),
    "state": GraphQLArgument(
        description="State that a server should have.", type=GraphQLString
    ),
    "error": GraphQLArgument(
        description="Set to true if you want only error states.",
        type=GraphQLBoolean,
    ),
}


def serverLogsField(models):
    return GraphQLField(
        GraphQLList(serverLogType),
        args=serverLogsFilters,
        resolver=lambda root, info, **args: fetch_server_logs(models, args),
    )
