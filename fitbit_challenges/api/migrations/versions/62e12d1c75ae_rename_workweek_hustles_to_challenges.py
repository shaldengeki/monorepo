"""rename workweek hustles to challenges

Revision ID: 62e12d1c75ae
Revises: eb246dcdc8c6
Create Date: 2023-05-24 01:36:16.758566

"""

from typing import Optional

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "62e12d1c75ae"
down_revision = "eb246dcdc8c6"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.rename_table("workweek_hustles", "challenges")
    op.add_column(
        "challenges", sa.Column("challenge_type", sa.Integer, default=0, nullable=True)
    )
    op.execute("UPDATE challenges SET challenge_type=0")
    op.alter_column(
        "challenges",
        "challenge_type",
        existing_server_default=0,  # type: ignore
        server_default=None,
        existing_type=sa.Integer,
        existing_nullable=True,
        nullable=False,
    )


def downgrade():
    op.drop_column("challenges", "challenge_type")
    op.rename_table("challenges", "workweek_hustles")
