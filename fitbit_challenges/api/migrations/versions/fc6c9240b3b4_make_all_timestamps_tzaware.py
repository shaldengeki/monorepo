"""make-all-timestamps-tzaware

Revision ID: fc6c9240b3b4
Revises: 30f47b7ec657
Create Date: 2023-06-17 23:07:34.431960

"""

from typing import Optional

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fc6c9240b3b4"
down_revision = "30f47b7ec657"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.alter_column(
        "users",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "synced_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=True,
    )
    op.alter_column(
        "subscription_notifications",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
    )
    op.alter_column(
        "subscription_notifications",
        "processed_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=True,
    )
    op.alter_column(
        "subscription_notifications",
        "date",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
    )
    op.alter_column(
        "user_activities",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
    )
    op.alter_column(
        "user_activities",
        "updated_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "users",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "synced_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
    op.alter_column(
        "subscription_notifications",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "subscription_notifications",
        "processed_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
    op.alter_column(
        "subscription_notifications",
        "date",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "user_activities",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "user_activities",
        "updated_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
