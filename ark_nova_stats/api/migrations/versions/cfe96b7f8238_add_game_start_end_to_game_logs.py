"""add-game-start-end-to-game-logs

Revision ID: cfe96b7f8238
Revises: b240d476fde9
Create Date: 2024-09-18 21:22:18.098754

"""

import json
import logging
from typing import Optional

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm

from ark_nova_stats.bga_log_parser.game_log import GameLog as BGAGameLog
from ark_nova_stats.models import GameLog as GameLogModel

# revision identifiers, used by Alembic.
revision = "cfe96b7f8238"
down_revision = "b240d476fde9"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.add_column(
        "game_logs",
        sa.Column("game_start", sa.DateTime, nullable=True),
    )
    op.add_column(
        "game_logs",
        sa.Column("game_end", sa.DateTime, nullable=True),
    )
    op.create_index(
        "game_logs_game_end",
        "game_logs",
        ["game_end"],
    )


def downgrade():
    op.drop_index("game_logs_game_end", "game_logs")
    op.drop_column("game_logs", "game_start")
    op.drop_column("game_logs", "game_end")
