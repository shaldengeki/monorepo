"""create-game-log-archives-table

Revision ID: 89684eb58df8
Revises: 10f0b2e2d286
Create Date: 2024-07-30 21:56:20.744980

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.functions import now

# revision identifiers, used by Alembic.
revision = "89684eb58df8"
down_revision = "10f0b2e2d286"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "game_log_archives",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("url", sa.UnicodeText, nullable=False),
        sa.Column("num_game_logs", sa.Integer, nullable=False),
        sa.Column("num_users", sa.Integer, nullable=False),
        sa.Column("last_game_log_id", sa.Integer),
        sa.Column("created_at", sa.DateTime, default=now, nullable=False),
    )

    op.create_index(
        "game_log_archives_created_at",
        "game_log_archives",
        ["created_at"],
    )


def downgrade():
    op.drop_index("game_log_archives_created_at", "game_log_archives")
    op.drop_table("game_log_archives")
