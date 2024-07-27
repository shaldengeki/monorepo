"""add-table-id-to-game-logs

Revision ID: 8c749a7279e7
Revises: 2ce11871a414
Create Date: 2024-07-27 18:20:31.263830

"""

import json

import sqlalchemy as sa
from alembic import op

from ark_nova_stats.bga_log_parser.game_log import GameLog as BGAGameLog
from ark_nova_stats.models import GameLog as GameLogModel

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
    for log_model in GameLogModel.query.all():
        parsed_log = BGAGameLog(**json.loads(log_model.log))
        table_ids = set(l.table_id for l in parsed_log.data.logs)
        if len(table_ids) != 1:
            raise RuntimeError(
                f"Log {log_model.id} is invalid: there must be exactly one table_id per game log, found: {table_ids}"
            )

        op.execute(
            f"update game_logs set bga_table_id={list(table_ids)[0]} where id = {log_model.id} limit 1"
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
