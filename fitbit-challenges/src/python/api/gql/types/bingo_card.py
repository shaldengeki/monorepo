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

from ....config import app, db
from ....models import Challenge, User, BingoCard, BingoTile, UnusedAmounts
from .user import user_type, fetch_current_user
from .challenge import (
    challenge_fields,
    ChallengeType,
)


def flipped_at_resolver(tile: BingoTile) -> Optional[int]:
    if tile.flipped_at is None:
        return tile.flipped_at
    return int(tile.flipped_at.timestamp())


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
            resolve=lambda bt, info, **args: flipped_at_resolver(bt),
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


def flip_bingo_tile(bingo_tile_model: Type[BingoTile], *args, **kwargs) -> BingoTile:
    tile_id = int(kwargs["id"])
    current_user = fetch_current_user(app, User)
    if current_user is None:
        raise ValueError("You must be signed in to flip a bingo tile.")

    tile = (
        bingo_tile_model.query.join(bingo_tile_model.bingo_card)
        .filter(bingo_tile_model.id == tile_id)
        .filter(BingoCard.user == current_user)
        .filter(BingoTile.flipped == False)
        .first()
    )
    if tile is None:
        raise ValueError(f"No bingo tile with id {tile_id} found.")

    unused_amounts = tile.bingo_card.unused_amounts()
    if tile.steps is not None and tile.steps > unused_amounts.steps:
        raise ValueError(f"You don't have enough unused steps to flip this tile!")
    elif (
        tile.active_minutes is not None
        and tile.active_minutes > unused_amounts.activeMinutes
    ):
        raise ValueError(
            f"You don't have enough unused active minutes to flip this tile!"
        )
    elif tile.distance_km is not None and tile.distance_km > unused_amounts.distanceKm:
        raise ValueError(f"You don't have enough unused kilometers to flip this tile!")

    tile.flip()
    db.session.add(tile)
    db.session.commit()
    return tile


def flip_bingo_tile_field(
    bingo_tile_model: Type[BingoTile],
) -> GraphQLField:
    return GraphQLField(
        bingo_tile_type,
        description="Flips a bingo tile.",
        args={
            "id": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="ID of the bingo tile to flip.",
            ),
        },
        resolve=lambda *args, **kwargs: flip_bingo_tile(
            bingo_tile_model, *args, **kwargs
        ),
    )


def finished_at_resolver(card: BingoCard) -> Optional[int]:
    finished_at = card.finished_at()
    if finished_at is None:
        return None

    return int(finished_at.timestamp())


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
            GraphQLNonNull(bingo_challenge_type),
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
        "finished": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="Whether the bingo card is completed.",
            resolve=lambda card, *args, **kwargs: card.finished(),
        ),
        "finishedAt": GraphQLField(
            GraphQLInt,
            description="When the bingo card was completed. Null if it wasn't.",
            resolve=lambda card, *args, **kwargs: finished_at_resolver(card),
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


def unused_amounts_resolver(
    app: Flask, challenge: Challenge, user_model: type[User]
) -> UnusedAmounts:
    current_user = fetch_current_user(app, user_model)
    if current_user is None:
        return UnusedAmounts(steps=None, activeMinutes=None, distanceKm=None)

    bingo_card = [
        card
        for card in challenge.bingo_cards
        if card.user.fitbit_user_id == current_user.fitbit_user_id
    ][0]

    return bingo_card.unused_amounts()


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
