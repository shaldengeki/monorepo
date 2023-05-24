from graphql import GraphQLObjectType, GraphQLSchema, GraphQLField, GraphQLString

from .types.challenge import challenges_field
from .types.workweek_hustle import create_workweek_hustle_field
from .types.weekend_warrior import create_weekend_warrior_field
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
                "challenges": challenges_field(models.Challenge),
                "activities": activities_field(models.UserActivity),
            },
        ),
        mutation=GraphQLObjectType(
            name="Mutation",
            fields={
                "createWeekendWarrior": create_weekend_warrior_field(models.Challenge),
                "createWorkweekHustle": create_workweek_hustle_field(models.Challenge),
                "createUserActivity": create_user_activity_field(models.UserActivity),
                "updateUserActivity": update_user_activity_field(models.UserActivity),
            },
        ),
    )
