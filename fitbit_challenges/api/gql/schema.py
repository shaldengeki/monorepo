from graphql import GraphQLObjectType, GraphQLSchema

from fitbit_challenges.api.gql.types.bingo_card import (
    bingo_challenge_field,
    flip_bingo_tile_field,
)
from fitbit_challenges.api.gql.types.challenge_user import (
    challenges_field,
    create_challenge_field,
    current_user_field,
    users_field,
)
from fitbit_challenges.api.gql.types.fitbit_authorization import (
    authorize_with_fitbit_field,
)
from fitbit_challenges.api.gql.types.user_activities import (
    activities_field,
    create_user_activity_field,
    update_user_activity_field,
)
from fitbit_challenges.models import (
    BingoTile,
    Challenge,
    ChallengeMembership,
    User,
    UserActivity,
)


def Schema(app):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="Query",
            fields={
                "challenges": challenges_field(Challenge),
                "activities": activities_field(UserActivity),
                "currentUser": current_user_field(app, User),
                "users": users_field(User),
                "bingoChallenge": bingo_challenge_field(Challenge),
            },
        ),
        mutation=GraphQLObjectType(
            name="Mutation",
            fields={
                "createChallenge": create_challenge_field(
                    Challenge, User, ChallengeMembership
                ),
                "createUserActivity": create_user_activity_field(UserActivity),
                "authWithFitbit": authorize_with_fitbit_field(app),
                "updateUserActivity": update_user_activity_field(UserActivity),
                "flipBingoTile": flip_bingo_tile_field(BingoTile),
            },
        ),
    )
