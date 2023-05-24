from graphql import GraphQLObjectType, GraphQLSchema

from .types.challenge import challenges_field, create_challenge_field
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
                "createChallenge": create_challenge_field(models.Challenge),
                "createUserActivity": create_user_activity_field(models.UserActivity),
                "updateUserActivity": update_user_activity_field(models.UserActivity),
            },
        ),
    )
