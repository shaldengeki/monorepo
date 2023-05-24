import datetime
from graphql import (
    GraphQLArgument,
    GraphQLField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLString,
)
from typing import Any, Type

from ...config import db
from .challenge import Challenge, ChallengeType, challenge_type


def create_weekend_warrior(
    challenge_model: Type[Challenge], args: dict[str, Any]
) -> Challenge:
    # Round to nearest hour.
    startAt = int(int(args["startAt"]) / 3600) * 3600

    # Two days after starting.
    endAt = startAt + 2 * 24 * 60 * 60

    challenge = challenge_model(
        challenge_type=ChallengeType.WEEKEND_WARRIOR.value,
        users=",".join(args["users"]),
        start_at=datetime.datetime.utcfromtimestamp(startAt),
        end_at=datetime.datetime.utcfromtimestamp(endAt),
    )
    db.session.add(challenge)
    db.session.commit()
    return challenge


def create_weekend_warrior_field(
    challenge_model: Type[Challenge],
) -> GraphQLField:
    return GraphQLField(
        challenge_type,
        description="Create a Weekend Warrior challenge.",
        args={
            "users": GraphQLArgument(
                GraphQLList(GraphQLString),
                description="List of usernames participating in the challenge.",
            ),
            "startAt": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Time the challenge should start, in unix epoch time.",
            ),
        },
        resolve=lambda root, info, **args: create_weekend_warrior(
            challenge_model, args
        ),
    )
