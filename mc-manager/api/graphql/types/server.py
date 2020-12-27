import datetime
from graphql import (
    GraphQLArgument,
    GraphQLObjectType,
    GraphQLField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLString,
)
from sqlalchemy import desc

from ...app import db
from .server_log import serverLogStateEnum


def latestBackupResolver(server):
    if not server.backups:
        return None
    return server.backups[0]


def latestLogResolver(server):
    if not server.logs:
        return None
    return server.logs[0]


def serverTypeResolver():
    from .server_log import serverLogType
    from .server_backup import serverBackupType

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
            resolve=lambda server, info, **args: server.backups,
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


def fetch_servers(models, params):
    query_obj = models.Server.query
    if params.get("earliestDate", False):
        query_obj = query_obj.filter(
            models.Server.created
            >= datetime.datetime.utcfromtimestamp(int(params["earliestDate"]))
        )
    if params.get("latestDate", False):
        query_obj = query_obj.filter(
            models.Server.created
            <= datetime.datetime.utcfromtimestamp(int(params["latestDate"]))
        )
    if params.get("createdBy", False):
        query_obj = query_obj.filter(models.Server.created_by == params["createdBy"])
    if params.get("name", False):
        query_obj = query_obj.filter(models.Server.name == params["name"])
    if params.get("port", False):
        query_obj = query_obj.filter(models.Server.port == int(params["port"]))
    if params.get("timezone", False):
        query_obj = query_obj.filter(models.Server.timezone == params["timezone"])
    if params.get("zipfile", False):
        query_obj = query_obj.filter(models.Server.zipfile == params["zipfile"])

    return query_obj.order_by(desc(models.Server.created)).all()


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


def serversField(models):
    return GraphQLField(
        GraphQLList(serverType),
        args=serversFilters,
        resolve=lambda root, info, **args: fetch_servers(models, args),
    )


def create_server(models, args):
    server = models.Server(
        created_by=args["createdBy"],
        name=args["name"],
        port=int(args["port"]),
        timezone=args["timezone"],
        zipfile=args["zipfile"],
        motd=args.get("motd"),
        memory=args["memory"],
    )
    db.session.add(server)

    server_log = models.ServerLog(server=server, state="created")
    db.session.add(server_log)

    db.session.commit()
    return server


def createServerField(models):
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
        resolve=lambda root, info, **args: create_server(models, args),
    )
