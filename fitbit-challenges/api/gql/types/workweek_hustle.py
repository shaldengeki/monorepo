import datetime
from graphql import (
    GraphQLArgument,
    GraphQLObjectType,
    GraphQLField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLString,
)
from sqlalchemy import desc
from typing import Any, Type

from ...config import db
from ...models import WorkweekHustle


def workweek_hustle_fields() -> dict[str, GraphQLField]:
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The id of the Workweek Hustle challenge.",
        ),
        "users": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The users participating in the challenge, as a comma-separated string.",
        ),
        "createdAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the Workweek Hustle was created, in unix epoch time.",
            resolve=lambda server, info, **args: int(server.created_at.timestamp()),
        ),
        "startAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The start datetime of the challenge, in unix epoch time.",
            resolve=lambda server, info, **args: int(server.start_at.timestamp()),
        ),
        "endAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The end datetime of the challenge, in unix epoch time.",
            resolve=lambda server, info, **args: int(server.end_at.timestamp()),
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
    challenge = workweek_hustle_model(
        users=args["users"],
        start_at=datetime.datetime.utcfromtimestamp(int(args["startAt"])),
        end_at=datetime.datetime.utcfromtimestamp(int(args["endAt"])),
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
                GraphQLNonNull(GraphQLString),
                description="Comma-separated list of usernames participating in the challenge.",
            ),
            "startAt": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Time the challenge should start, in unix epoch time.",
            ),
            "endAt": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Time the challenge should end, in unix epoch time.",
            ),
        },
        resolve=lambda root, info, **args: create_workweek_hustle(
            workweek_hustle_model, args
        ),
    )
