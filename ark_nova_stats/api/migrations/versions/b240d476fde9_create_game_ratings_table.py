"""create-game-ratings-table

Revision ID: b240d476fde9
Revises: 896829658716
Create Date: 2024-08-24 02:07:57.634111

"""

import sqlalchemy as sa
from alembic import op
from typing import Optional
from sqlalchemy.sql.functions import now

# revision identifiers, used by Alembic.
revision = "b240d476fde9"
down_revision = "896829658716"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.create_table(
        "game_ratings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("bga_table_id", sa.Integer, nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("prior_elo", sa.Integer, nullable=True),
        sa.Column("new_elo", sa.Integer, nullable=True),
        sa.Column("prior_arena_elo", sa.Integer, nullable=True),
        sa.Column("new_arena_elo", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, default=now, nullable=False),
    )

    op.create_index(
        "game_ratings_bga_table_id_user_id",
        "game_ratings",
        ["bga_table_id", "user_id"],
        unique=True,
    )

    op.create_index(
        "game_ratings_user_id_bga_table_id_created_at",
        "game_ratings",
        ["user_id", "bga_table_id", "created_at"],
    )


def downgrade():
    op.drop_index("game_ratings_user_id_bga_table_id_created_at", "game_ratings")
    op.drop_index("game_ratings_bga_table_id_user_id", "game_ratings")
    op.drop_table("game_ratings")
