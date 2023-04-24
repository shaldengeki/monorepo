import datetime
from graphql import (
    GraphQLArgument,
    GraphQLObjectType,
    GraphQLField,
    GraphQLFloat,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLString,
)
from sqlalchemy import desc
from sqlalchemy.sql.functions import now
from typing import Any, Type

from ...config import db
from ...models import UserActivity


def user_activity_fields() -> dict[str, GraphQLField]:
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The id of the logged user activity.",
        ),
        "user": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The user who logged the activity.",
        ),
        "createdAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the activity log was created, in unix epoch time.",
            resolve=lambda ua, info, **args: int(ua.created_at.timestamp()),
        ),
        "updatedAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the activity log was last updated, in unix epoch time.",
            resolve=lambda ua, info, **args: int(ua.updated_at.timestamp()),
        ),
        "recordDate": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The day that the activity log was recorded for, in unix epoch time.",
            resolve=lambda ua, info, **args: int(
                datetime.datetime.fromordinal(ua.record_date.toordinal()).timestamp()
            ),
        ),
        "steps": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of steps logged.",
            resolve=lambda ua, info, **args: int(ua.steps),
        ),
        "activeMinutes": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of active minutes logged.",
            resolve=lambda ua, info, **args: int(ua.active_minutes),
        ),
        "distanceKm": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The distance, in kilometers, logged.",
            resolve=lambda ua, info, **args: round(ua.distance_km, 2),
        ),
    }


user_activity_type = GraphQLObjectType(
    "UserActivity",
    description="An activity log recorded by a user.",
    fields=user_activity_fields,
)


def fetch_user_activities(
    user_activity_model: Type[UserActivity], params: dict[str, Any]
):
    query_obj = user_activity_model.query
    if params.get("users", []):
        query_obj = query_obj.filter(user_activity_model.user.in_(params["users"]))
    if params.get("recordedAfter", []):
        query_obj = query_obj.filter(
            user_activity_model.record_date
            >= datetime.datetime.utcfromtimestamp(int(params["recordedAfter"]))
        )
    if params.get("recordedBefore", []):
        query_obj = query_obj.filter(
            user_activity_model.record_date
            <= datetime.datetime.utcfromtimestamp(int(params["recordedBefore"]))
        )
    return query_obj.order_by(desc(user_activity_model.created_at)).all()


user_activities_filters: dict[str, GraphQLArgument] = {
    "users": GraphQLArgument(
        GraphQLList(GraphQLString),
        description="Users whose activities should be fetched.",
    ),
    "recordedAfter": GraphQLArgument(
        GraphQLInt,
        description="The earliest date for which a returned activity should be recorded.",
    ),
    "recordedBefore": GraphQLArgument(
        GraphQLInt,
        description="The latest date for which a returned activity should be recorded.",
    ),
}


def activities_field(user_activity_model: Type[UserActivity]) -> GraphQLField:
    return GraphQLField(
        GraphQLList(user_activity_type),
        args=user_activities_filters,
        resolve=lambda root, info, **args: fetch_user_activities(
            user_activity_model, args
        ),
    )


def create_user_activity(
    user_activity_model: Type[UserActivity], args: dict[str, Any]
) -> UserActivity:
    user_activity = user_activity_model(
        record_date=datetime.date.fromtimestamp(int(args["recordDate"])),
        user=args["user"],
        steps=int(args["steps"]),
        active_minutes=int(args["activeMinutes"]),
        distance_km=int(args["distanceKm"]),
    )
    db.session.add(user_activity)

    db.session.commit()
    return user_activity


def create_user_activity_field(
    user_activity_model: Type[UserActivity],
) -> GraphQLField:
    return GraphQLField(
        user_activity_type,
        description="Creates a new user activity.",
        args={
            "recordDate": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Date on which the activity was performed.",
            ),
            "user": GraphQLArgument(
                GraphQLNonNull(GraphQLString),
                description="User for whom the record is being created.",
            ),
            "steps": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Number of steps.",
            ),
            "activeMinutes": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Number of steps.",
            ),
            "distanceKm": GraphQLArgument(
                GraphQLNonNull(GraphQLFloat),
                description="Distance, in kilometers.",
            ),
        },
        resolve=lambda root, info, **args: create_user_activity(
            user_activity_model, args
        ),
    )


def update_user_activity(
    user_activity_model: Type[UserActivity], args: dict[str, Any]
) -> UserActivity:
    user_activity = user_activity_model.query.filter(
        user_activity_model.id == int(args["id"])
    ).first()
    if user_activity is None:
        raise ValueError(
            f"User activity with id {args['id']} doesn't exist, and can't be updated."
        )

    if "recordDate" in args:
        user_activity.record_date = datetime.date.fromtimestamp(int(args["recordDate"]))

    if "user" in args:
        user_activity.user = args.get("user")

    if "steps" in args:
        user_activity.steps = int(args.get("steps"))

    if "activeMinutes" in args:
        user_activity.active_minutes = int(args.get("activeMinutes"))

    if "distanceKm" in args:
        user_activity.distance_km = float(args.get("distanceKm"))

    user_activity.updated_at = now()

    db.session.add(user_activity)
    db.session.commit()
    return user_activity


def update_user_activity_field(
    user_activity_model: Type[UserActivity],
) -> GraphQLField:
    return GraphQLField(
        user_activity_type,
        description="Updates an existing user activity.",
        args={
            "id": GraphQLArgument(
                GraphQLNonNull(GraphQLInt), description="ID of the user activity."
            ),
            "recordDate": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Date on which the activity was performed.",
            ),
            "user": GraphQLArgument(
                GraphQLNonNull(GraphQLString),
                description="User for whom the record is being updated.",
            ),
            "steps": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Number of steps.",
            ),
            "activeMinutes": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Number of steps.",
            ),
            "distanceKm": GraphQLArgument(
                GraphQLNonNull(GraphQLFloat),
                description="Distance, in kilometers.",
            ),
        },
        resolve=lambda root, info, **args: update_user_activity(
            user_activity_model, args
        ),
    )
