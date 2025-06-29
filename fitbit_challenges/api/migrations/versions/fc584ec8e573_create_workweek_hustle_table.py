"""create workweek_hustle table

Revision ID: fc584ec8e573
Revises:
Create Date: 2023-04-15 20:14:18.608315

"""

from typing import Optional

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.functions import now

# revision identifiers, used by Alembic.
revision = "fc584ec8e573"
down_revision: Optional[str] = None
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.create_table(
        "workweek_hustles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("users", sa.Unicode(500), nullable=False),
        sa.Column("created_at", sa.DateTime, default=now, nullable=False),
        sa.Column("start_at", sa.DateTime, nullable=False),
        sa.Column("end_at", sa.DateTime, nullable=False),
    )

    op.create_index("workweek_hustles_start_at", "workweek_hustles", ["start_at"])


def downgrade():
    op.drop_table("workweek_hustles")
