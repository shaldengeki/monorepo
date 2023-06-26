import dataclasses
import decimal
from flask import Flask
from graphql import (
    GraphQLArgument,
    GraphQLBoolean,
    GraphQLObjectType,
    GraphQLField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
)
from typing import Any, Optional, Type
from sqlalchemy import desc

from ....config import app
from ....models import Challenge, User
from .user import user_type, fetch_current_user
from .challenge import (
    challenge_type,
    challenge_fields,
    challenges_filters,
    ChallengeType,
)


def bingo_tile_fields() -> dict[str, GraphQLField]:
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The id of the bingo tile.",
        ),
        "steps": GraphQLField(
            GraphQLInt,
            description="The number of steps required.",
        ),
        "activeMinutes": GraphQLField(
            GraphQLInt,
            description="The number of active minutes required.",
            resolve=lambda bt, *args, **kwargs: bt.active_minutes,
        ),
        "distanceKm": GraphQLField(
            GraphQLInt,
            description="The distance, in kilometers, required.",
            resolve=lambda bt, *args, **kwargs: bt.distance_km,
        ),
        "coordinateX": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The x-coordinate of this tile.",
            resolve=lambda bt, *args, **kwargs: bt.coordinate_x,
        ),
        "coordinateY": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The y-coordinate of this tile.",
            resolve=lambda bt, *args, **kwargs: bt.coordinate_y,
        ),
        "bonusType": GraphQLField(
            GraphQLInt,
            description="What kind of bonus this tile had.",
            resolve=lambda bt, *args, **kwargs: bt.bonus_type,
        ),
        "bonusAmount": GraphQLField(
            GraphQLInt,
            description="The amount to award for the bonus.",
            resolve=lambda bt, *args, **kwargs: bt.bonus_amount,
        ),
        "flipped": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the tile is flipped.",
        ),
        "flippedAt": GraphQLField(
            GraphQLInt,
            description="The datetime that the tile was flipped, in unix epoch time.",
            resolve=lambda bt, info, **args: int(bt.flipped_at.timestamp()),
        ),
        "requiredForWin": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the tile is required for a win.",
            resolve=lambda bt, *args, **kwargs: bt.required_for_win,
        ),
        "createdAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the bingo tile was created, in unix epoch time.",
            resolve=lambda bt, info, **args: int(bt.created_at.timestamp()),
        ),
        "bingoCard": GraphQLField(
            GraphQLNonNull(bingo_card_type),
            description="The bingo card for this tile.",
            resolve=lambda bt, *args, **kwargs: bt.bingo_card,
        ),
    }


bingo_tile_type = GraphQLObjectType(
    "BingoTile",
    description="A bingo tile on a bingo card.",
    fields=bingo_tile_fields,
)


def bingo_card_fields() -> dict[str, GraphQLField]:
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The id of the bingo card.",
        ),
        "user": GraphQLField(
            GraphQLNonNull(user_type),
            description="The user who is filling this bingo card out.",
        ),
        "challenge": GraphQLField(
            GraphQLNonNull(challenge_type),
            description="The challenge that this bingo card is a part of.",
        ),
        "rows": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of rows of this card.",
        ),
        "columns": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of columns of this card.",
        ),
        "createdAt": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The date that the card was created, in unix epoch time.",
            resolve=lambda card, info, **args: int(card.created_at.timestamp()),
        ),
        "tiles": GraphQLField(
            GraphQLNonNull(GraphQLList(bingo_tile_type)),
            description="The bingo tiles belonging to this card.",
            resolve=lambda card, *args, **kwargs: card.bingo_tiles,
        ),
    }


bingo_card_type = GraphQLObjectType(
    "BingoCard",
    description="A bingo card.",
    fields=bingo_card_fields,
)


def unused_amounts_fields() -> dict[str, GraphQLField]:
    return {
        "steps": GraphQLField(
            GraphQLInt,
            description="The number of unused steps",
        ),
        "activeMinutes": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The number of unused active minutes",
        ),
        "distanceKm": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The unused distance, in kilometers",
        ),
    }


unused_amounts_type = GraphQLObjectType(
    "UnusedAmounts",
    description="Unused amounts for a challenge.",
    fields=unused_amounts_fields,
)


@dataclasses.dataclass
class UnusedAmounts:
    steps: Optional[int]
    activeMinutes: Optional[int]
    distanceKm: Optional[decimal.Decimal]


def unused_amounts_resolver(
    app: Flask, challenge: Challenge, user_model: type[User]
) -> UnusedAmounts:
    current_user = fetch_current_user(app, user_model)
    if current_user is None:
        return UnusedAmounts(steps=None, activeMinutes=None, distanceKm=None)

    # Sum up the total user's resources.
    total_steps = 0
    total_active_minutes = 0
    total_distance_km = decimal.Decimal(0)
    for activity in challenge.activities_for_user(current_user):
        total_steps += activity.steps
        total_active_minutes += activity.active_minutes
        total_distance_km += activity.distance_km

    # Subtract out the user's used steps.
    bingo_card = [
        card
        for card in challenge.bingo_cards
        if card.user.fitbit_user_id == current_user.fitbit_user_id
    ][0]
    flipped_tiles = [tile for tile in bingo_card.bingo_tiles if tile.flipped]
    for tile in flipped_tiles:
        if tile.steps is not None:
            total_steps -= tile.steps
        if tile.active_minutes is not None:
            total_active_minutes -= tile.active_minutes
        if tile.distance_km is not None:
            total_distance_km -= tile.distance_km

    return UnusedAmounts(
        steps=total_steps,
        activeMinutes=total_active_minutes,
        distanceKm=total_distance_km,
    )


def bingo_challenge_fields() -> dict[str, GraphQLField]:
    fields = challenge_fields()
    fields.update(
        {
            "bingoCards": GraphQLField(
                GraphQLNonNull(GraphQLList(bingo_card_type)),
                description="The cards that are part of this bingo challenge.",
                resolve=lambda challenge, *args, **kwargs: challenge.bingo_cards,
            ),
            "unusedAmounts": GraphQLField(
                unused_amounts_type,
                description="The number of unused resources the current user has to spend.",
                resolve=lambda challenge, *args, **kwargs: unused_amounts_resolver(
                    app, challenge, User
                ),
            ),
        }
    )
    return fields


bingo_challenge_type = GraphQLObjectType(
    "BingoChallenge",
    description="A bingo challenge.",
    fields=bingo_challenge_fields,
)


def fetch_bingo_challenge(
    challenge_model: Type[Challenge], params: dict[str, Any]
) -> Optional[Challenge]:
    return (
        challenge_model.query.filter(
            challenge_model.challenge_type == ChallengeType.BINGO.value
        ).filter(challenge_model.id == params["id"])
    ).first()


bingo_challenge_filters: dict[str, GraphQLArgument] = {
    "id": GraphQLArgument(
        GraphQLNonNull(GraphQLInt),
        description="ID of the bingo challenge.",
    ),
}


def bingo_challenge_field(challenge_model: type[Challenge]) -> GraphQLField:
    return GraphQLField(
        bingo_challenge_type,
        args=bingo_challenge_filters,
        resolve=lambda root, info, **args: fetch_bingo_challenge(challenge_model, args),
    )
