"""alter-game-log-archives-type-field-enum

Revision ID: fef90e3dfd97
Revises: 89684eb58df8
Create Date: 2024-08-03 18:31:10.362460

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fef90e3dfd97"
down_revision = "89684eb58df8"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "game_log_archives",
        "archive_type",
        type_=sa.Integer,
        server_default=0,
        nullable=False,
        existing_type=sa.UnicodeText,
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "game_log_archives",
        "archive_type",
        type_=sa.UnicodeText,
        nullable=False,
        existing_type=sa.Integer,
        existing_nullable=False,
    )
