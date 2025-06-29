import datetime
from typing import Iterable

from graphql import (
    GraphQLArgument,
    GraphQLBoolean,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLString,
)
from sqlalchemy import desc

from mc_manager.api.models import ServerBackup, ServerLog
from mc_manager.config import db

serverLogStateEnum = GraphQLEnumType(
    "ServerLogState",
    description="State that a server can be in",
    values={
        "created": GraphQLEnumValue(
            "created", description="Server is queued to be started"
        ),
        "start_started": GraphQLEnumValue(
            "start_started", description="Server is starting"
        ),
        "started": GraphQLEnumValue(
            "started", description="Server is currently running"
        ),
        "restore_queued": GraphQLEnumValue(
            "restore_queued", description="Server restoration from backup is queued"
        ),
        "restore_started": GraphQLEnumValue(
            "restore_started",
            description="Server restoration from backup is in-progress",
        ),
        "stop_queued": GraphQLEnumValue(
            "stop_queued", description="Server is queued to be stopped"
        ),
        "stop_started": GraphQLEnumValue(
            "stop_started", description="Server is being stopped"
        ),
        "stopped": GraphQLEnumValue("stopped", description="Server is not running"),
    },
)


def serverLogResolver():
    from mc_manager.api.gql.types.server import serverType
    from mc_manager.api.gql.types.server_backup import serverBackupType

    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt), description="The id of the log."
        ),
        "server": GraphQLField(
            GraphQLNonNull(serverType),
            description="The server this log belongs to.",
        ),
        "created": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the log was recorded, in unix epoch time.",
            resolve=lambda transaction, info, **args: int(
                transaction.created.timestamp()
            ),
        ),
        "state": GraphQLField(
            GraphQLNonNull(serverLogStateEnum),
            description="The recorded state of the server.",
        ),
        "error": GraphQLField(
            GraphQLString, description="The error (if any) encountered by the server."
        ),
        "backup": GraphQLField(
            serverBackupType, description="The backup associated with this server log."
        ),
    }


serverLogType = GraphQLObjectType(
    "ServerLog",
    description="The state of a Server, recorded at a point in time.",
    fields=serverLogResolver,
)


def fetch_server_logs(params) -> Iterable[ServerLog]:
    query_obj = db.select(ServerLog)
    if params.get("earliestDate", False):
        query_obj = query_obj.filter(
            ServerLog.created
            >= datetime.datetime.utcfromtimestamp(int(params["earliestDate"]))
        )
    if params.get("latestDate", False):
        query_obj = query_obj.filter(
            ServerLog.created
            <= datetime.datetime.utcfromtimestamp(int(params["latestDate"]))
        )
    if params.get("serverId", False):
        query_obj = query_obj.filter(ServerLog.server_id == params["serverId"])
    if params.get("state", False):
        query_obj = query_obj.filter(ServerLog.state == params["state"])
    if params.get("error", False):
        query_obj = query_obj.filter(ServerLog.error != None)

    return db.session.execute(
        query_obj.order_by(desc(ServerLog.created)).all()
    ).scalars()


serverLogsFilters = {
    "earliestDate": GraphQLArgument(
        GraphQLInt, description="Earliest creation date that a server should have."
    ),
    "latestDate": GraphQLArgument(
        GraphQLInt, description="Latest creation date that a server should have."
    ),
    "serverId": GraphQLArgument(
        GraphQLInt,
        description="ID of the server.",
    ),
    "state": GraphQLArgument(
        GraphQLString,
        description="State that a server should have.",
    ),
    "error": GraphQLArgument(
        GraphQLBoolean,
        description="Set to true if you want only error states.",
    ),
}


def serverLogsField():
    return GraphQLField(
        GraphQLList(serverLogType),
        args=serverLogsFilters,
        resolve=lambda root, info, **args: fetch_server_logs(args),
    )


def create_server_log(args):
    backup = None
    if args.get("backupId") is not None:
        backup = db.session.execute(
            db.select(ServerBackup)
            .filter(ServerBackup.id == int(args.get("backupId")))
            .first()
        ).scalar_one()

    server_log = ServerLog(
        server_id=args["serverId"],
        state=args["state"],
        error=args.get("error"),
        backup=backup,
    )
    db.session.add(server_log)

    db.session.commit()
    return server_log


def createServerLogField():
    return GraphQLField(
        serverLogType,
        description="Create a server log for a given server.",
        args={
            "serverId": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Server ID that the log is being recorded for.",
            ),
            "state": GraphQLArgument(
                GraphQLNonNull(serverLogStateEnum), description="State of the server."
            ),
            "error": GraphQLArgument(
                GraphQLString,
                description="Error message (if any) that the server has presented.",
            ),
            "backupId": GraphQLArgument(
                GraphQLInt,
                description="ID of the backup that should be associated with this server log.",
            ),
        },
        resolve=lambda root, info, **args: create_server_log(args),
    )
