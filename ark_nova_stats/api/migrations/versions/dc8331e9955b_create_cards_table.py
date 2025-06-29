"""create-cards-table

Revision ID: dc8331e9955b
Revises: fef90e3dfd97
Create Date: 2024-08-12 16:11:42.008947

"""

import sqlalchemy as sa
from alembic import op
from typing import Optional
from sqlalchemy.sql.functions import now

# revision identifiers, used by Alembic.
revision = "dc8331e9955b"
down_revision = "fef90e3dfd97"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.create_table(
        "cards",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.UnicodeText, nullable=False),
        sa.Column("bga_id", sa.UnicodeText, nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime, default=now, nullable=False),
    )

    op.create_index(
        "cards_bga_id",
        "cards",
        ["bga_id"],
        unique=True,
    )


def downgrade():
    op.drop_index("cards_bga_id", "cards")
    op.drop_table("cards")
