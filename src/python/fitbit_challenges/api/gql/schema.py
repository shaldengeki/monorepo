from graphql import GraphQLObjectType, GraphQLSchema

from .types.bingo_card import bingo_challenge_field, flip_bingo_tile_field
from .types.challenge import challenges_field, create_challenge_field
from .types.fitbit_authorization import authorize_with_fitbit_field
from .types.user import current_user_field, users_field
from .types.user_activities import (
    activities_field,
    create_user_activity_field,
    update_user_activity_field,
)


def Schema(models, app):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="Query",
            fields={
                "challenges": challenges_field(models.Challenge),
                "activities": activities_field(models.UserActivity),
                "currentUser": current_user_field(app, models.User),
                "users": users_field(models.User),
                "bingoChallenge": bingo_challenge_field(models.Challenge),
            },
        ),
        mutation=GraphQLObjectType(
            name="Mutation",
            fields={
                "createChallenge": create_challenge_field(
                    models.Challenge, models.User, models.ChallengeMembership
                ),
                "createUserActivity": create_user_activity_field(models.UserActivity),
                "authWithFitbit": authorize_with_fitbit_field(app),
                "updateUserActivity": update_user_activity_field(models.UserActivity),
                "flipBingoTile": flip_bingo_tile_field(models.BingoTile),
            },
        ),
    )
