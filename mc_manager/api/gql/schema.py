from graphql import GraphQLObjectType, GraphQLSchema

from mc_manager.api.gql.types import (
    createServerBackupField,
    createServerField,
    createServerLogField,
    deleteServerBackupField,
    serverBackupsField,
    serverLogsField,
    serversField,
    updateServerBackupField,
)


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
