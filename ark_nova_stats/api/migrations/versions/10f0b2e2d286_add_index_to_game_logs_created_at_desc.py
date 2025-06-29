"""add-index-to-game-logs-created-at-desc

Revision ID: 10f0b2e2d286
Revises: bd2396f61798
Create Date: 2024-07-29 18:27:12.635973

"""

from typing import Optional

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "10f0b2e2d286"
down_revision = "bd2396f61798"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.create_index(
        "game_logs_created_at",
        "game_logs",
        ["created_at"],
    )


def downgrade():
    op.drop_index("game_logs_created_at", "game_logs")
