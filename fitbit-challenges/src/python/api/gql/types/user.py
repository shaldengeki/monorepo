from flask import Flask, session
from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLString,
)
from typing import Type, Optional

from ....models import User
from .user_activities import user_activity_type


def synced_at_resolver(user: User) -> Optional[int]:
    if user.synced_at is None:
        return None

    return int(user.synced_at.timestamp())


def user_fields() -> dict[str, GraphQLField]:
    from .challenge import challenge_type

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
        "syncedAt": GraphQLField(
            GraphQLInt,
            description="The date that the user's data was last synced, in unix epoch time.",
            resolve=lambda user, *args, **kwargs: synced_at_resolver(user),
        ),
        "activities": GraphQLField(
            GraphQLNonNull(GraphQLList(user_activity_type)),
            description="The activities recorded by this user.",
            resolve=lambda user, *args, **kwargs: sorted(
                user.activities, key=lambda a: a.created_at, reverse=True
            ),
        ),
        "challenges": GraphQLField(
            GraphQLNonNull(GraphQLList(challenge_type)),
            description="The list of challenges this user has ever participated in.",
            resolve=lambda user, *args, **kwargs: sorted(
                user.challenges(), key=lambda c: c.created_at, reverse=True
            ),
        ),
        "activeChallenges": GraphQLField(
            GraphQLNonNull(GraphQLList(challenge_type)),
            description="The list of challenges this user is currently participating in.",
            resolve=lambda user, *args, **kwargs: sorted(
                user.active_challenges(), key=lambda c: c.created_at, reverse=True
            ),
        ),
        "pastChallenges": GraphQLField(
            GraphQLNonNull(GraphQLList(challenge_type)),
            description="The list of past challenges this user has participated in.",
            resolve=lambda user, *args, **kwargs: sorted(
                user.past_challenges(), key=lambda c: c.created_at, reverse=True
            ),
        ),
    }


user_type = GraphQLObjectType(
    "User",
    description="A user.",
    fields=user_fields,
)


def fetch_users(user_model: Type[User]) -> list[User]:
    return user_model.query.all()


def users_field(user_model: Type[User]) -> GraphQLField:
    return GraphQLField(
        GraphQLList(user_type),
        resolve=lambda root, info, **args: fetch_users(user_model),
    )


def fetch_current_user(app: Flask, user_model: Type[User]) -> Optional[User]:
    if app.config["DEBUG"]:
        # In development, user is logged in.
        return user_model.query.first()

    if "fitbit_user_id" not in session:
        return None
    user = user_model.query.filter(
        user_model.fitbit_user_id == session["fitbit_user_id"]
    ).first()
    if not user:
        session.pop("fitbit_user_id")
        return None
    return user


def current_user_field(app: Flask, user_model: Type[User]) -> GraphQLField:
    return GraphQLField(
        user_type,
        resolve=lambda root, info, **args: fetch_current_user(app, user_model),
    )
