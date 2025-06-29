"""create subjects table

Revision ID: 9da1de15cd6a
Revises:
Create Date: 2022-07-21 04:15:20.943034

"""

import datetime

import sqlalchemy as sa
from alembic import op
from typing import Optional

# revision identifiers, used by Alembic.
revision = "9da1de15cd6a"
down_revision: Optional[str] = None
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "created", sa.DateTime, nullable=False, default=datetime.datetime.utcnow
        ),
        sa.Column("name", sa.Unicode(2000), nullable=False),
    )
    op.create_index(
        "subjects_name",
        "subjects",
        ["name"],
    )


def downgrade():
    op.drop_table("subjects")
