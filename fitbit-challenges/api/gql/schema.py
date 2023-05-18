from graphql import GraphQLObjectType, GraphQLSchema, GraphQLField, GraphQLString

from .types.workweek_hustle import challenges_field, create_workweek_hustle_field
from .types.user_activities import (
    activities_field,
    create_user_activity_field,
    update_user_activity_field,
)


def Schema(models):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="Query",
            fields={
                "challenges": challenges_field(models.WorkweekHustle),
                "activities": activities_field(models.UserActivity),
            },
        ),
        mutation=GraphQLObjectType(
            name="Mutation",
            fields={
                "createWorkweekHustle": create_workweek_hustle_field(
                    models.WorkweekHustle
                ),
                "createUserActivity": create_user_activity_field(models.UserActivity),
                "updateUserActivity": update_user_activity_field(models.UserActivity),
            },
        ),
    )
