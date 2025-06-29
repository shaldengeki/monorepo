"""alter-game-logs-game-start-end-non-nullable

Revision ID: 142c66849d87
Revises: cfe96b7f8238
Create Date: 2024-09-18 22:03:59.380204

"""

import sqlalchemy as sa
from alembic import op
from typing import Optional

# revision identifiers, used by Alembic.
revision = "142c66849d87"
down_revision = "cfe96b7f8238"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.alter_column(
        "game_logs",
        "game_start",
        nullable=False,
        existing_nullable=True,
    )
    op.alter_column(
        "game_logs",
        "game_end",
        nullable=False,
        existing_nullable=True,
    )


def downgrade():
    op.alter_column(
        "game_logs",
        "game_start",
        nullable=True,
        existing_nullable=False,
    )
    op.alter_column(
        "game_logs",
        "game_end",
        nullable=True,
        existing_nullable=False,
    )
