"""create-game-logs

Revision ID: 2ce11871a414
Revises:
Create Date: 2024-07-18 00:11:53.246321

"""

from typing import Optional

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.functions import now

# revision identifiers, used by Alembic.
revision = "2ce11871a414"
down_revision = None
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.create_table(
        "game_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("log", sa.UnicodeText, nullable=False),
        sa.Column("created_at", sa.DateTime, default=now, nullable=False),
    )


def downgrade():
    op.drop_table("game_logs")
