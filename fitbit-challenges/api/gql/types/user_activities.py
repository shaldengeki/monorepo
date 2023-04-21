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
            resolve=lambda ua, info, **args: int(ua.record_date.timestamp()),
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
        query_obj = query_obj.filter(user_activity_model.user in params["users"])
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
