"""create servers table

Revision ID: 9d3e78009e2e
Revises:
Create Date: 2020-12-08 11:48:47.669297

"""

from typing import Optional

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9d3e78009e2e"
down_revision: Optional[str] = None
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.create_table(
        "servers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("created", sa.DateTime, nullable=False),
        sa.Column("created_by", sa.Unicode(100), nullable=False),
        sa.Column("name", sa.Unicode(100), nullable=False),
        sa.Column("port", sa.Integer, nullable=False),
        sa.Column("timezone", sa.Unicode(100), nullable=False),
        sa.Column("zipfile", sa.Unicode(100), nullable=False),
        sa.Column("motd", sa.Unicode(100), nullable=True),
        sa.Column("memory", sa.Unicode(3), nullable=False),
    )


def downgrade():
    op.drop_table("servers")
