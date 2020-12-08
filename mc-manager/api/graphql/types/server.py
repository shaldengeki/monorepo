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

serverType = GraphQLObjectType(
    "Server",
    description="A Minecraft server that players can connect to.",
    fields=lambda: {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt), description="The id of the transaction."
        ),
        "created": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the server was created, in unix epoch time.",
            resolver=lambda transaction, info, **args: int(
                transaction.created.timestamp()
            ),
        ),
        "createdBy": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The username of the player who created the server.",
            resolver=lambda transaction, info, **args: transaction.created_by,
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
    },
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
        description="Earliest creation date that a server should have.", type=GraphQLInt
    ),
    "latestDate": GraphQLArgument(
        description="Latest creation date that a server should have.", type=GraphQLInt
    ),
    "createdBy": GraphQLArgument(
        description="Username that the server should have been created by.",
        type=GraphQLString,
    ),
    "name": GraphQLArgument(
        description="Name that a server should have.", type=GraphQLString
    ),
    "port": GraphQLArgument(
        description="Port that a server should be running on.",
        type=GraphQLInt,
    ),
    "timezone": GraphQLArgument(
        description="Timezone that a server should have.", type=GraphQLString
    ),
    "zipfile": GraphQLArgument(
        description="Name of modpack zipfile that a server should have.",
        type=GraphQLString,
    ),
}


def serversField(models):
    return GraphQLField(
        GraphQLList(serverType),
        args=serversFilters,
        resolver=lambda root, info, **args: fetch_servers(models, args),
    )
