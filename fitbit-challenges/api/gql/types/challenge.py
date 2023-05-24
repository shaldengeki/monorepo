import datetime
from enum import Enum
from graphql import (
    GraphQLArgument,
    GraphQLBoolean,
    GraphQLObjectType,
    GraphQLField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLString,
)
from sqlalchemy import desc
from sqlalchemy.sql import func
from typing import Any, Type

from ...config import db
from ...models import Challenge, UserActivity
from .user_activities import user_activity_type


def activities_resolver(challenge: Challenge, info, **args) -> list[UserActivity]:
    return (
        UserActivity.query.filter(UserActivity.user.in_(challenge.users.split(",")))
        .filter(
            func.date_trunc("day", UserActivity.record_date)
            >= func.date_trunc("day", challenge.start_at)
        )
        .filter(UserActivity.record_date < challenge.end_at)
        .filter(UserActivity.created_at < challenge.seal_at)
        .order_by(desc(UserActivity.created_at))
        .all()
    )


def challenge_fields() -> dict[str, GraphQLField]:
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The id of the challenge.",
        ),
        "challengeType": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The type of the challenge.",
            resolve=lambda challenge, info, **args: challenge.challenge_type,
        ),
        "users": GraphQLField(
            GraphQLNonNull(GraphQLList(GraphQLString)),
            description="The users participating in the challenge, as a comma-separated string.",
            resolve=lambda challenge, info, **args: challenge.users.split(","),
        ),
        "createdAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the challenge was created, in unix epoch time.",
            resolve=lambda challenge, info, **args: int(
                challenge.created_at.timestamp()
            ),
        ),
        "startAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The start datetime of the challenge, in unix epoch time.",
            resolve=lambda challenge, info, **args: int(challenge.start_at.timestamp()),
        ),
        "endAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The end datetime of the challenge, in unix epoch time.",
            resolve=lambda challenge, info, **args: int(challenge.end_at.timestamp()),
        ),
        "ended": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the challenge is ended.",
            resolve=lambda challenge, info, **args: bool(challenge.ended),
        ),
        "sealAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The datetime that the challenge refuses additional data, in unix epoch time.",
            resolve=lambda challenge, info, **args: int(challenge.seal_at.timestamp()),
        ),
        "sealed": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the challenge is sealed.",
            resolve=lambda challenge, info, **args: bool(challenge.sealed),
        ),
        "activities": GraphQLField(
            GraphQLNonNull(GraphQLList(user_activity_type)),
            description="The activities recorded as part of this challenge.",
            resolve=activities_resolver,
        ),
    }


challenge_type = GraphQLObjectType(
    "Challenge",
    description="A challenge.",
    fields=challenge_fields,
)


def fetch_challenges(challenge_model: Type[Challenge], params: dict[str, Any]):
    query_obj = challenge_model.query
    if params.get("id", False):
        query_obj = query_obj.filter(challenge_model.id == params["id"])
    return query_obj.order_by(desc(challenge_model.start_at)).all()


challenges_filters: dict[str, GraphQLArgument] = {
    "id": GraphQLArgument(
        GraphQLInt,
        description="ID of the challenge.",
    ),
}


def challenges_field(challenge_model: Type[Challenge]) -> GraphQLField:
    return GraphQLField(
        GraphQLList(challenge_type),
        args=challenges_filters,
        resolve=lambda root, info, **args: fetch_challenges(challenge_model, args),
    )


class ChallengeType(Enum):
    WORKWEEK_HUSTLE = 0
    WEEKEND_WARRIOR = 1
