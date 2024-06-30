import datetime

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

from mc_manager.api.config import db
from mc_manager.api.models.server_backup import ServerBackup

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
    from mc_manager.api.gql.types.server import serverType

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


def fetch_server_backups(params):
    query_obj = ServerBackup.query
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
        query_obj = query_obj.filter(
            ServerBackup.server_id == params["serverId"]
        )
    if params.get("state", False):
        query_obj = query_obj.filter(ServerBackup.state == params["state"])
    if params.get("error", False):
        query_obj = query_obj.filter(ServerBackup.error != None)
    if params.get("remote_path", False):
        query_obj = query_obj.filter(
            ServerBackup.remote_path == params["remotePath"]
        )

    if params.get("after", False):
        query_obj = query_obj.filter(ServerBackup.id > int(params["after"]))

    query_obj = query_obj.order_by(desc(ServerBackup.created))
    limit = min((100, int(params["limit"])))
    query_obj = query_obj.limit(limit)

    return query_obj.all()


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
    server_backup = ServerBackup.query.filter(
        ServerBackup.id == params["id"]
    ).first()
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
    server_backup = ServerBackup.query.filter(
        ServerBackup.id == params["id"]
    ).first()
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
