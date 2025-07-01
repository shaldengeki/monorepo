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

from mc_manager.api.models import Server, ServerBackup, ServerLog
from mc_manager.config import db


def latestBackupResolver(server):
    if not server.backups:
        return None
    return server.backups[0]


def latestLogResolver(server):
    if not server.logs:
        return None
    return server.logs[0]


def backupsResolver(server, args) -> Iterable[ServerBackup]:
    query_obj = db.select(ServerBackup).filter(ServerBackup.server_id == server.id)
    if args.get("after", False):
        query_obj = query_obj.filter(ServerBackup.id > int(args["after"]))

    query_obj = query_obj.order_by(desc(ServerBackup.created))

    limit = min((100, int(args["limit"])))
    query_obj = query_obj.limit(limit)

    return db.session.execute(query_obj.all()).scalars()


def serverTypeResolver():
    from mc_manager.api.gql.types import serverBackupType

    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt), description="The id of the server."
        ),
        "created": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the server was created, in unix epoch time.",
            resolve=lambda server, info, **args: int(server.created.timestamp()),
        ),
        "createdBy": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The username of the player who created the server.",
            resolve=lambda server, info, **args: server.created_by,
        ),
        "name": GraphQLField(
            GraphQLNonNull(GraphQLString), description="The name of the server."
        ),
        "port": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The port that the server runs on.",
        ),
        "timezone": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The timezone that the server is set in.",
        ),
        "zipfile": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The name of the zipped modpack file, downloaded from CurseForge.",
        ),
        "motd": GraphQLField(
            GraphQLString,
            description="The message displayed to users on the server list.",
        ),
        "memory": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The amount of memory to allocate to the server.",
        ),
        "logs": GraphQLField(
            GraphQLList(serverLogType),
            description="Logs associated with the server.",
            resolve=lambda server, info, **args: server.logs,
        ),
        "latestLog": GraphQLField(
            serverLogType,
            description="Latest log associated with the server.",
            resolve=lambda server, info, **args: latestLogResolver(server),
        ),
        "backups": GraphQLField(
            GraphQLList(serverBackupType),
            description="Backups associated with the server.",
            args={
                "after": GraphQLArgument(
                    GraphQLInt,
                    description="The ID after which results should be displayed.",
                ),
                "limit": GraphQLArgument(
                    GraphQLInt,
                    description="The total number of results to return. Defaults to 10, with the maximum being 100.",
                    default_value=100,
                ),
            },
            resolve=lambda server, info, **args: backupsResolver(server, args),
        ),
        "latestBackup": GraphQLField(
            serverBackupType,
            description="Latest backup associated with the server.",
            resolve=lambda server, info, **args: latestBackupResolver(server),
        ),
    }


serverType = GraphQLObjectType(
    "Server",
    description="A Minecraft server that players can connect to.",
    fields=serverTypeResolver,
)


def fetch_servers(params) -> Iterable[Server]:
    query_obj = db.select(Server)
    if params.get("earliestDate", False):
        query_obj = query_obj.filter(
            Server.created
            >= datetime.datetime.utcfromtimestamp(int(params["earliestDate"]))
        )
    if params.get("latestDate", False):
        query_obj = query_obj.filter(
            Server.created
            <= datetime.datetime.utcfromtimestamp(int(params["latestDate"]))
        )
    if params.get("createdBy", False):
        query_obj = query_obj.filter(Server.created_by == params["createdBy"])
    if params.get("name", False):
        query_obj = query_obj.filter(Server.name == params["name"])
    if params.get("port", False):
        query_obj = query_obj.filter(Server.port == int(params["port"]))
    if params.get("timezone", False):
        query_obj = query_obj.filter(Server.timezone == params["timezone"])
    if params.get("zipfile", False):
        query_obj = query_obj.filter(Server.zipfile == params["zipfile"])

    return db.session.execute(query_obj.order_by(desc(Server.created)).all()).scalars()


serversFilters = {
    "earliestDate": GraphQLArgument(
        GraphQLInt,
        description="Earliest creation date that a server should have.",
    ),
    "latestDate": GraphQLArgument(
        GraphQLInt,
        description="Latest creation date that a server should have.",
    ),
    "createdBy": GraphQLArgument(
        GraphQLString,
        description="Username that the server should have been created by.",
    ),
    "name": GraphQLArgument(
        GraphQLString,
        description="Name that a server should have.",
    ),
    "port": GraphQLArgument(
        GraphQLInt,
        description="Port that a server should be running on.",
    ),
    "timezone": GraphQLArgument(
        GraphQLString,
        description="Timezone that a server should have.",
    ),
    "zipfile": GraphQLArgument(
        GraphQLString,
        description="Name of modpack zipfile that a server should have.",
    ),
}


def serversField():
    return GraphQLField(
        GraphQLList(serverType),
        args=serversFilters,
        resolve=lambda root, info, **args: fetch_servers(args),
    )


def create_server(args):
    server = Server(
        created_by=args["createdBy"],
        name=args["name"],
        port=int(args["port"]),
        timezone=args["timezone"],
        zipfile=args["zipfile"],
        motd=args.get("motd"),
        memory=args["memory"],
    )
    db.session.add(server)

    server_log = ServerLog(server=server, state="created")
    db.session.add(server_log)

    db.session.commit()
    return server


def createServerField():
    return GraphQLField(
        serverType,
        description="Create a Minecraft server.",
        args={
            "createdBy": GraphQLArgument(
                GraphQLNonNull(GraphQLString),
                description="Minecraft username creating the server.",
            ),
            "name": GraphQLArgument(
                GraphQLNonNull(GraphQLString), description="Name of the server."
            ),
            "port": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Port that the server should run on.",
            ),
            "timezone": GraphQLArgument(
                GraphQLNonNull(GraphQLString),
                description="Timezone that the server should run in.",
            ),
            "zipfile": GraphQLArgument(
                GraphQLNonNull(GraphQLString),
                description="Filename of the CurseForge zipfile that this server runs.",
            ),
            "motd": GraphQLArgument(
                GraphQLString,
                description="MOTD displayed by this server on a server listing.",
            ),
            "memory": GraphQLArgument(
                GraphQLNonNull(GraphQLString),
                description="Amount of memory to allocate to the server.",
            ),
        },
        resolve=lambda root, info, **args: create_server(args),
    )


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
    from mc_manager.api.gql.types import serverBackupType, serverType

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


serverBackupStateEnum = GraphQLEnumType(
    "ServerBackupState",
    description="State that a server backup can be in",
    values={
        "created": GraphQLEnumValue(
            "created", description="Server backup is queued to be started"
        ),
        "started": GraphQLEnumValue(
            "started", description="Server backup is currently running"
        ),
        "completed": GraphQLEnumValue(
            "completed", description="Server backup is completed"
        ),
        "failed": GraphQLEnumValue("failed", description="Server backup failed"),
        "deleted": GraphQLEnumValue(
            "deleted", description="Server backup has been deleted"
        ),
    },
)


def serverBackupResolver():
    from mc_manager.api.gql.types import serverType

    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt), description="The id of the log."
        ),
        "server": GraphQLField(
            GraphQLNonNull(serverType),
            description="The server this backup belongs to.",
        ),
        "created": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the log was recorded, in unix epoch time.",
            resolve=lambda transaction, info, **args: int(
                transaction.created.timestamp()
            ),
        ),
        "state": GraphQLField(
            GraphQLNonNull(serverBackupStateEnum),
            description="The recorded state of the server backup.",
        ),
        "error": GraphQLField(
            GraphQLString,
            description="The error (if any) encountered by the server backup.",
        ),
        "remotePath": GraphQLField(
            GraphQLString,
            description="The URL of the remote path that the backup is located at.",
            resolve=lambda backup, info, **args: backup.remote_path,
        ),
    }


serverBackupType = GraphQLObjectType(
    "ServerBackup",
    description="A backup for a Server, uploaded to a remote destination.",
    fields=serverBackupResolver,
)


def fetch_server_backups(params) -> Iterable[ServerBackup]:
    query_obj = db.select(ServerBackup)
    if params.get("earliestDate", False):
        query_obj = query_obj.filter(
            ServerBackup.created
            >= datetime.datetime.utcfromtimestamp(int(params["earliestDate"]))
        )
    if params.get("latestDate", False):
        query_obj = query_obj.filter(
            ServerBackup.created
            <= datetime.datetime.utcfromtimestamp(int(params["latestDate"]))
        )
    if params.get("serverId", False):
        query_obj = query_obj.filter(ServerBackup.server_id == params["serverId"])
    if params.get("state", False):
        query_obj = query_obj.filter(ServerBackup.state == params["state"])
    if params.get("error", False):
        query_obj = query_obj.filter(ServerBackup.error != None)
    if params.get("remote_path", False):
        query_obj = query_obj.filter(ServerBackup.remote_path == params["remotePath"])

    if params.get("after", False):
        query_obj = query_obj.filter(ServerBackup.id > int(params["after"]))

    query_obj = query_obj.order_by(desc(ServerBackup.created))
    limit = min((100, int(params["limit"])))
    query_obj = query_obj.limit(limit)

    return db.session.execute(query_obj.all()).scalars()


serverBackupsFilters = {
    "after": GraphQLArgument(
        GraphQLInt, description="The ID after which results should be displayed."
    ),
    "earliestDate": GraphQLArgument(
        GraphQLInt,
        description="Earliest creation date that a server backup should have.",
    ),
    "error": GraphQLArgument(
        GraphQLBoolean,
        description="Set to true if you want only error states.",
    ),
    "latestDate": GraphQLArgument(
        GraphQLInt, description="Latest creation date that a server backup should have."
    ),
    "limit": GraphQLArgument(
        GraphQLInt,
        description="The total number of results to return. Defaults to 10, with the maximum being 100.",
        default_value=100,
    ),
    "remotePath": GraphQLArgument(
        GraphQLString,
        description="URL of the remote path that the backup is located at.",
    ),
    "serverId": GraphQLArgument(
        GraphQLInt,
        description="ID of the server backup.",
    ),
    "state": GraphQLArgument(
        serverBackupStateEnum,
        description="State that a server backup should have.",
    ),
}


def serverBackupsField():
    return GraphQLField(
        GraphQLList(serverBackupType),
        args=serverBackupsFilters,
        resolve=lambda root, info, **args: fetch_server_backups(args),
    )


def create_server_backup(args):
    server_backup = ServerBackup(
        server_id=args["serverId"],
        state=args.get("state", "created"),
        error=args.get("error"),
        remote_path=args.get("remotePath"),
    )
    db.session.add(server_backup)

    db.session.commit()
    return server_backup


def createServerBackupField():
    return GraphQLField(
        serverBackupType,
        description="Create a server backup entry for a given server.",
        args={
            "serverId": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Server ID that the backup is being generated for.",
            ),
            "state": GraphQLArgument(
                serverBackupStateEnum, description="State of the server backup."
            ),
            "error": GraphQLArgument(
                GraphQLString,
                description="Error message (if any) that the server has presented.",
            ),
            "remotePath": GraphQLArgument(
                GraphQLString,
                description="URL to the remote location of the server backup.",
            ),
        },
        resolve=lambda root, info, **args: create_server_backup(args),
    )


def update_server_backup(params):
    server_backup = db.session.execute(
        db.select(ServerBackup).filter(ServerBackup.id == params["id"]).first()
    ).scalar_one_or_none()
    if server_backup is None:
        raise ValueError(
            f"Server backup with id {params['id']} doesn't exist, and can't be updated."
        )

    if "state" in params:
        server_backup.state = params.get("state")

    if "error" in params:
        server_backup.error = params["error"]

    if "remotePath" in params:
        server_backup.remote_path = params["remotePath"]

    db.session.add(server_backup)
    db.session.commit()

    return server_backup


def updateServerBackupField():
    return GraphQLField(
        serverBackupType,
        description="Update a server backup entry for a given server.",
        args={
            "id": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="ID of the server backup.",
            ),
            "state": GraphQLArgument(
                serverBackupStateEnum, description="State of the server backup."
            ),
            "error": GraphQLArgument(
                GraphQLString,
                description="Error message (if any) that the server has presented.",
            ),
            "remotePath": GraphQLArgument(
                GraphQLString,
                description="URL to the remote location of the server backup.",
            ),
        },
        resolve=lambda root, info, **args: update_server_backup(args),
    )


def delete_server_backup(params):
    server_backup = db.session.execute(
        db.select(ServerBackup).filter(ServerBackup.id == params["id"]).first()
    ).scalar_one_or_none()
    if server_backup is None:
        raise ValueError(
            f"Server backup with id {params['id']} doesn't exist, and can't be deleted."
        )

    db.session.delete(server_backup)
    db.session.commit()

    return server_backup


def deleteServerBackupField():
    return GraphQLField(
        serverBackupType,
        description="Delete a server backup entry for a given server.",
        args={
            "id": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="ID of the server backup.",
            ),
        },
        resolve=lambda root, info, **args: delete_server_backup(args),
    )
