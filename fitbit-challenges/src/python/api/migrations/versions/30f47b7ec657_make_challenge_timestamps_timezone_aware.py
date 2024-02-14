"""make challenge timestamps timezone-aware

Revision ID: 30f47b7ec657
Revises: 8c49dbd35d2f
Create Date: 2023-06-17 22:59:31.453367

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "30f47b7ec657"
down_revision = "8c49dbd35d2f"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "challenges",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
    )
    op.alter_column(
        "challenges",
        "start_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
    )
    op.alter_column(
        "challenges",
        "end_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "challenges",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "challenges",
        "start_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "challenges",
        "end_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
