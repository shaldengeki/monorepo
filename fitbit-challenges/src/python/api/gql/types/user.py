from flask import session
from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLString,
)
from sqlalchemy import desc
from typing import Type, Optional

from ....models import User, UserActivity
from .user_activities import user_activity_type


def activities_resolver(user: User, info, **args) -> list[UserActivity]:
    return (
        UserActivity.query.filter(UserActivity.user == user.fitbit_user_id)
        .order_by(desc(UserActivity.created_at))
        .all()
    )


def user_fields() -> dict[str, GraphQLField]:
    return {
        "fitbitUserId": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The fitbit user ID of the user.",
            resolve=lambda user, info, **args: user.fitbit_user_id,
        ),
        "displayName": GraphQLField(
            GraphQLNonNull(GraphQLString),
            description="The user's display name.",
            resolve=lambda user, info, **args: user.display_name,
        ),
        "createdAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the user was created, in unix epoch time.",
            resolve=lambda user, info, **args: int(user.created_at.timestamp()),
        ),
        "activities": GraphQLField(
            GraphQLNonNull(GraphQLList(user_activity_type)),
            description="The activities recorded by this user.",
            resolve=activities_resolver,
        ),
    }


user_type = GraphQLObjectType(
    "User",
    description="A user.",
    fields=user_fields,
)


def fetch_current_user(user_model: Type[User]) -> Optional[User]:
    if "fitbit_user_id" not in session:
        return None
    user = user_model.query.filter(
        user_model.fitbit_user_id == session["fitbit_user_id"]
    ).first()
    if not user:
        session.pop("fitbit_user_id")
        return None
    return user


def current_user_field(user_model: Type[User]) -> GraphQLField:
    return GraphQLField(
        user_type,
        resolve=lambda root, info, **args: fetch_current_user(user_model),
    )
