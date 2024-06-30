from graphql import GraphQLObjectType, GraphQLSchema

from mc_manager.api.gql.types.server import createServerField, serversField
from mc_manager.api.gql.types.server_backup import (
    createServerBackupField,
    deleteServerBackupField,
    serverBackupsField,
    updateServerBackupField,
)
from mc_manager.api.gql.types.server_log import createServerLogField, serverLogsField


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
                "deleteServerBackup": deleteServerBackupField(models),
                "updateServerBackup": updateServerBackupField(models),
            },
        ),
    )
