"""add-table-id-to-game-logs

Revision ID: 8c749a7279e7
Revises: 2ce11871a414
Create Date: 2024-07-27 18:20:31.263830

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8c749a7279e7"
down_revision = "2ce11871a414"
branch_labels = None
depends_on = None


def upgrade():
    # First, add a non-unique column.
    op.add_column(
        "game_logs",
        sa.Column(
            "bga_table_id",
            sa.Integer,
            unique=True,
        ),
    )

    op.create_index(
        "game_logs_bga_table_id",
        "game_logs",
        ["bga_table_id"],
        unique=True,
    )


def downgrade():
    op.drop_index("game_logs_bga_table_id", "game_logs")
    op.drop_column("game_logs", "bga_table_id")
