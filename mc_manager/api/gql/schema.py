from graphql import GraphQLObjectType, GraphQLSchema

from mc_manager.api.gql.types.server import createServerField, serversField
from mc_manager.api.gql.types.server_backup import (
    createServerBackupField,
    deleteServerBackupField,
    serverBackupsField,
    updateServerBackupField,
)
from mc_manager.api.gql.types.server_log import createServerLogField, serverLogsField


def Schema():
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="RootQueryType",
            fields={
                "servers": serversField(),
                "serverBackups": serverBackupsField(),
                "serverLogs": serverLogsField(),
            },
        ),
        mutation=GraphQLObjectType(
            name="RootMutationType",
            fields={
                "createServer": createServerField(),
                "createServerBackup": createServerBackupField(),
                "createServerLog": createServerLogField(),
                "deleteServerBackup": deleteServerBackupField(),
                "updateServerBackup": updateServerBackupField(),
            },
        ),
    )
