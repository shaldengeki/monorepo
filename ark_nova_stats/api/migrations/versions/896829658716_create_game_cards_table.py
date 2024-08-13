"""create-game-cards-table

Revision ID: 896829658716
Revises: dc8331e9955b
Create Date: 2024-08-12 16:18:39.585795

"""

import json

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm
from sqlalchemy.sql.functions import now

from ark_nova_stats.bga_log_parser.game_log import GameLog as BGAGameLog
from ark_nova_stats.models import Card as CardModel
from ark_nova_stats.models import CardPlay as CardPlayModel
from ark_nova_stats.models import GameLog as GameLogModel

# revision identifiers, used by Alembic.
revision = "896829658716"
down_revision = "dc8331e9955b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "game_log_cards",
        sa.Column("game_log_id", sa.Integer, nullable=False),
        sa.Column("card_id", sa.Integer, nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("move", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, default=now, nullable=False),
    )

    op.create_index(
        "game_log_cards_card_id_game_log_id",
        "game_log_cards",
        ["card_id", "game_log_id"],
        unique=True,
    )

    op.create_index(
        "game_log_cards_game_log_id_move",
        "game_log_cards",
        ["game_log_id", "move"],
    )

    op.create_index(
        "game_log_cards_user_id",
        "game_log_cards",
        ["user_id"],
    )

    # Next, process game logs and add cards.
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    cards = {}

    for log_model in session.query(GameLogModel):
        parsed_log = BGAGameLog(**json.loads(log_model.log))
        # First, create underlying card models.
        for play in parsed_log.data.card_plays:
            if play.card.id not in cards:
                # Check to see if it exists.
                find_card = (
                    CardModel.query.where(CardModel.bga_id == play.card.id)
                    .limit(1)
                    .all()
                )
                if find_card is None:
                    card = CardModel(  # type: ignore
                        name=play.card.name, bga_id=play.card.id
                    )
                    session.add(card)
                else:
                    card = find_card[0]

                cards[card.bga_id] = card

            session.add(
                CardPlayModel(  # type: ignore
                    game_log_id=log_model.id,
                    card=cards[play.card.id],
                    user_id=play.player.id,
                    move=play.move,
                )
            )

    session.commit()


def downgrade():
    op.drop_index("game_log_cards_user_id", "game_log_cards")
    op.drop_index("game_log_cards_game_log_id_move", "game_log_cards")
    op.drop_index("game_log_cards_card_id_game_log_id", "game_log_cards")
    op.drop_table("game_log_cards")
