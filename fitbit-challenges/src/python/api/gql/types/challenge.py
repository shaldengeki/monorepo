import datetime
from flask import Flask
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
import random
from sqlalchemy import desc
from typing import Any, Optional, Type

from ....config import app, db
from ....models import Challenge, ChallengeMembership, BingoCard, User, ChallengeType
from .user_activities import user_activity_type
from .user import user_type, fetch_current_user


def winners_resolver(challenge: Challenge) -> list[User]:
    rankings: list[User]
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    if challenge.challenge_type in (
        ChallengeType.WEEKEND_WARRIOR.value,
        ChallengeType.WORKWEEK_HUSTLE.value,
    ):
        if not challenge.ended:
            return []

        challenge_progress = sorted(
            (
                (user, totals.steps)
                for user, totals in challenge.total_amounts().items()
            ),
            key=lambda x: x[1],
            reverse=True,
        )
        rankings = [x[0] for x in challenge_progress][0:3]
    elif challenge.challenge_type == ChallengeType.BINGO.value:
        bingo_progress: list[tuple[User, tuple[int, Optional[datetime.timedelta]]]] = []
        for user in challenge.users:
            card = next(
                card for card in user.bingo_cards if card.challenge_id == challenge.id
            )
            finished_at = card.finished_at()
            if finished_at is None:
                continue

            bingo_progress.append(
                (
                    user,
                    (len(list(card.flipped_victory_tiles())), now - finished_at),
                )
            )
        if not bingo_progress:
            return []

        rankings = [
            x[0] for x in sorted(bingo_progress, key=lambda x: x[1], reverse=True)
        ][0:3]
    else:
        raise ValueError(
            f"Invalid challenge type {challenge.challenge_type} for challenge #{challenge.id}!"
        )
    return rankings


def current_user_placement_resolver(challenge: Challenge, app: Flask) -> Optional[int]:
    current_user = fetch_current_user(app, User)
    if current_user is None:
        return None

    if current_user not in challenge.users:
        return None

    winners = winners_resolver(challenge)
    for idx, winner in enumerate(winners):
        if winner.fitbit_user_id == current_user.fitbit_user_id:
            return idx + 1

    return None


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
            GraphQLNonNull(GraphQLList(user_type)),
            description="The users participating in the challenge.",
            resolve=lambda challenge, info, **args: challenge.users_list,
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
        "started": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the challenge has started.",
            resolve=lambda challenge, info, **args: bool(challenge.started),
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
            resolve=lambda challenge, *args, **kwargs: challenge.activities(),
        ),
        "winners": GraphQLField(
            GraphQLList(user_type),
            description="A list of the winners for this challenge, in ranked order.",
            resolve=lambda challenge, *args, **kwargs: winners_resolver(challenge),
        ),
        "currentUserPlacement": GraphQLField(
            GraphQLInt,
            description="An integer representing the current user's win ranking.",
            resolve=lambda challenge, *args, **kwargs: current_user_placement_resolver(
                challenge, app
            ),
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


def create_challenge(
    challenge_model: Type[Challenge],
    user_model: Type[User],
    challenge_membership_model: Type[ChallengeMembership],
    args: dict[str, Any],
) -> Challenge:
    # Round to nearest hour.
    startAt = int(int(args["startAt"]) / 3600) * 3600

    # Make sure each user exists.
    users = []
    not_found_user_ids = []
    for fitbit_user_id in args["users"]:
        user = user_model.query.filter(
            user_model.fitbit_user_id == fitbit_user_id
        ).first()
        if user is None:
            not_found_user_ids.append(fitbit_user_id)
            continue
        users.append(user)

    if not_found_user_ids:
        raise ValueError(
            f"Could not find users with ids: {', '.join(not_found_user_ids)}"
        )

    challenge_type = int(args["challengeType"])
    if ChallengeType.WORKWEEK_HUSTLE.value == challenge_type:
        # Five days after starting.
        endAt = startAt + 5 * 24 * 60 * 60
    elif ChallengeType.WEEKEND_WARRIOR.value == challenge_type:
        # Two days after starting.
        endAt = startAt + 2 * 24 * 60 * 60
    elif ChallengeType.BINGO.value == challenge_type:
        # Round end time to the nearest hour.
        endAt = int(int(args["endAt"]) / 3600) * 3600
    else:
        raise ValueError(f"Invalid challenge type!")

    challenge = challenge_model(
        challenge_type=challenge_type,
        start_at=datetime.datetime.utcfromtimestamp(startAt),
        end_at=datetime.datetime.utcfromtimestamp(endAt),
    )
    for user in users:
        membership = challenge_membership_model(user=user, challenge=challenge)
        challenge.user_memberships.append(membership)
        db.session.add(membership)

    db.session.add(challenge)
    db.session.commit()

    if ChallengeType.BINGO.value == challenge_type:
        pattern = random.choice(BingoCard.PATTERNS)
        users = User.query.filter(User.fitbit_user_id.in_(args["users"])).all()
        for user in users:
            card = BingoCard()
            card.create_for_user_and_challenge(
                user=user,
                challenge=challenge,
                start=datetime.datetime.fromtimestamp(
                    startAt, tz=datetime.timezone.utc
                ),
                end=datetime.datetime.fromtimestamp(endAt, tz=datetime.timezone.utc),
                pattern=pattern,
            )
            db.session.add(card)

    db.session.commit()

    return challenge


def create_challenge_field(
    challenge_model: Type[Challenge],
    user_model: Type[User],
    challenge_membership_model: Type[ChallengeMembership],
) -> GraphQLField:
    return GraphQLField(
        challenge_type,
        description="Create a challenge.",
        args={
            "users": GraphQLArgument(
                GraphQLList(GraphQLString),
                description="List of usernames participating in the challenge.",
            ),
            "challengeType": GraphQLArgument(
                GraphQLNonNull(GraphQLInt), description="Type of challenge to create."
            ),
            "startAt": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Time the challenge should start, in unix epoch time.",
            ),
            "endAt": GraphQLArgument(
                GraphQLInt,
                description="Time the challenge should end, in unix epoch time.",
            ),
        },
        resolve=lambda root, info, **args: create_challenge(
            challenge_model, user_model, challenge_membership_model, args
        ),
    )
