"""alter-game-log-archives-type-field-enum

Revision ID: fef90e3dfd97
Revises: 89684eb58df8
Create Date: 2024-08-03 18:31:10.362460

"""

from typing import Optional

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fef90e3dfd97"
down_revision = "89684eb58df8"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.drop_column("game_log_archives", "archive_type")
    op.add_column(
        "game_log_archives",
        sa.Column(
            "archive_type",
            sa.Integer,
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column("game_log_archives", "archive_type")
    op.add_column(
        "game_log_archives",
        sa.Column(
            "archive_type",
            sa.UnicodeText,
            nullable=False,
        ),
    )
