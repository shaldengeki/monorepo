from graphql import GraphQLField, GraphQLObjectType, GraphQLSchema

from .types.challenge import challenges_field, create_challenge_field
from .types.user import current_user_field, users_field
from .types.user_activities import (
    activities_field,
    create_user_activity_field,
    update_user_activity_field,
)
from .types.fitbit_authorization import authorize_with_fitbit_field


def Schema(models, app):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="Query",
            fields={
                "challenges": challenges_field(models.Challenge),
                "activities": activities_field(models.UserActivity),
                "currentUser": current_user_field(app, models.User),
                "users": users_field(models.User),
            },
        ),
        mutation=GraphQLObjectType(
            name="Mutation",
            fields={
                "createChallenge": create_challenge_field(models.Challenge),
                "createUserActivity": create_user_activity_field(models.UserActivity),
                "authWithFitbit": authorize_with_fitbit_field(app),
                "updateUserActivity": update_user_activity_field(models.UserActivity),
            },
        ),
    )
