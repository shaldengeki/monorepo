"""create-bingo-tile

Revision ID: d2401a8f7896
Revises: 9dafaf879435
Create Date: 2023-06-19 01:22:41.532924

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.functions import now


# revision identifiers, used by Alembic.
revision = "d2401a8f7896"
down_revision = "9dafaf879435"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "bingo_tiles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("bingo_card_id", sa.Integer, nullable=False),
        sa.Column("steps", sa.Integer, nullable=True),
        sa.Column("active_minutes", sa.Integer, nullable=True),
        sa.Column("distance_km", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("coordinate_x", sa.Integer, nullable=False),
        sa.Column("coordinate_y", sa.Integer, nullable=False),
        sa.Column("bonus_type", sa.Integer, nullable=True),
        sa.Column("bonus_amount", sa.Integer, nullable=True),
        sa.Column("flipped", sa.Boolean, nullable=False, default=False),
        sa.Column("flipped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("required_for_win", sa.Boolean, nullable=False, default=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), default=now, nullable=False
        ),
    )
    op.create_index(
        "bingo_tiles_bingo_card_id_coordinate_y_coordinate_x",
        "bingo_tiles",
        columns=["bingo_card_id", "coordinate_y", "coordinate_x"],
        unique=True,
    )


def downgrade():
    op.drop_index("bingo_tiles_bingo_card_id_coordinate_y_coordinate_x", "bingo_tiles")
    op.drop_table("bingo_tiles")
