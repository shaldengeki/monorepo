import datetime
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
from ...models import WorkweekHustle, UserActivity
from .user_activities import user_activity_type


def activities_resolver(hustle: WorkweekHustle, info, **args) -> list[UserActivity]:
    return (
        UserActivity.query.filter(UserActivity.user.in_(hustle.users.split(",")))
        .filter(
            func.to_char(UserActivity.record_date, "%Y-%m-%d")
            >= func.to_char(hustle.start_at, "%Y-%m-%d")
        )
        .filter(UserActivity.record_date < hustle.end_at)
        .filter(UserActivity.created_at < hustle.seal_at)
        .order_by(desc(UserActivity.created_at))
        .all()
    )


def workweek_hustle_fields() -> dict[str, GraphQLField]:
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The id of the Workweek Hustle challenge.",
        ),
        "users": GraphQLField(
            GraphQLNonNull(GraphQLList(GraphQLString)),
            description="The users participating in the challenge, as a comma-separated string.",
            resolve=lambda hustle, info, **args: hustle.users.split(","),
        ),
        "createdAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the Workweek Hustle was created, in unix epoch time.",
            resolve=lambda hustle, info, **args: int(hustle.created_at.timestamp()),
        ),
        "startAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The start datetime of the challenge, in unix epoch time.",
            resolve=lambda hustle, info, **args: int(hustle.start_at.timestamp()),
        ),
        "endAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The end datetime of the challenge, in unix epoch time.",
            resolve=lambda hustle, info, **args: int(hustle.end_at.timestamp()),
        ),
        "ended": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the challenge is ended.",
            resolve=lambda hustle, info, **args: bool(hustle.ended),
        ),
        "sealAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The datetime that the challenge refuses additional data, in unix epoch time.",
            resolve=lambda hustle, info, **args: int(hustle.seal_at.timestamp()),
        ),
        "sealed": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the challenge is sealed.",
            resolve=lambda hustle, info, **args: bool(hustle.sealed),
        ),
        "activities": GraphQLField(
            GraphQLNonNull(GraphQLList(user_activity_type)),
            description="The activities recorded as part of this challenge.",
            resolve=activities_resolver,
        ),
    }


workweek_hustle_type = GraphQLObjectType(
    "WorkweekHustle",
    description="A Workweek Hustle challenge.",
    fields=workweek_hustle_fields,
)


def fetch_workweek_hustles(
    workweek_hustle_model: Type[WorkweekHustle], params: dict[str, Any]
):
    query_obj = workweek_hustle_model.query
    if params.get("id", False):
        query_obj = query_obj.filter(workweek_hustle_model.id == params["id"])
    return query_obj.order_by(desc(workweek_hustle_model.start_at)).all()


workweek_hustles_filters: dict[str, GraphQLArgument] = {
    "id": GraphQLArgument(
        GraphQLInt,
        description="ID of the challenge.",
    ),
}


def challenges_field(workweek_hustle_model: Type[WorkweekHustle]) -> GraphQLField:
    return GraphQLField(
        GraphQLList(workweek_hustle_type),
        args=workweek_hustles_filters,
        resolve=lambda root, info, **args: fetch_workweek_hustles(
            workweek_hustle_model, args
        ),
    )


def create_workweek_hustle(
    workweek_hustle_model: Type[WorkweekHustle], args: dict[str, Any]
) -> WorkweekHustle:
    # Round to nearest hour.
    startAt = int(int(args["startAt"]) / 3600) * 3600

    # Five days after starting.
    endAt = startAt + 5 * 24 * 60 * 60

    challenge = workweek_hustle_model(
        users=",".join(args["users"]),
        start_at=datetime.datetime.utcfromtimestamp(startAt),
        end_at=datetime.datetime.utcfromtimestamp(endAt),
    )
    db.session.add(challenge)
    db.session.commit()
    return challenge


def create_workweek_hustle_field(
    workweek_hustle_model: Type[WorkweekHustle],
) -> GraphQLField:
    return GraphQLField(
        workweek_hustle_type,
        description="Create a Workweek Hustle challenge.",
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
        resolve=lambda root, info, **args: create_workweek_hustle(
            workweek_hustle_model, args
        ),
    )
