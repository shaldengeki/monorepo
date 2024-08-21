"""create-game-cards-table

Revision ID: 896829658716
Revises: dc8331e9955b
Create Date: 2024-08-12 16:18:39.585795

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.functions import now

# revision identifiers, used by Alembic.
revision = "896829658716"
down_revision = "dc8331e9955b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "game_log_cards",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("game_log_id", sa.Integer, nullable=False),
        sa.Column("card_id", sa.Integer, nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("move", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, default=now, nullable=False),
    )

    op.create_index(
        "game_log_cards_card_id_game_log_id_move",
        "game_log_cards",
        ["card_id", "game_log_id", "move"],
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


def downgrade():
    op.drop_index("game_log_cards_user_id", "game_log_cards")
    op.drop_index("game_log_cards_game_log_id_move", "game_log_cards")
    op.drop_index("game_log_cards_card_id_game_log_id_move", "game_log_cards")
    op.drop_table("game_log_cards")
