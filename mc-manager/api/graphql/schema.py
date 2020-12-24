from graphql import GraphQLObjectType, GraphQLSchema
from .types.server import (
    serversField,
    createServerField,
)
from .types.server_log import (
    serverLogsField,
    createServerLogField,
)
from .types.server_backup import (
    serverBackupsField,
    createServerBackupField,
    updateServerBackupField,
)


def Schema(models):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="RootQueryType",
            fields={
                "servers": serversField(models),
                "serverBackups": serverBackupsField(models),
                "serverLogs": serverLogsField(models),
            },
        ),
        mutation=GraphQLObjectType(
            name="RootMutationType",
            fields={
                "createServer": createServerField(models),
                "createServerBackup": createServerBackupField(models),
                "createServerLog": createServerLogField(models),
                "updateServerBackup": updateServerBackupField(models),
            },
        ),
    )
