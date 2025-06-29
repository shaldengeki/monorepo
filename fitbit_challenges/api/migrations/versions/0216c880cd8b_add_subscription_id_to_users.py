"""add subscription_id to users

Revision ID: 0216c880cd8b
Revises: fe51b503d5ed
Create Date: 2023-05-28 16:22:44.511833

"""

import sqlalchemy as sa
from alembic import op
from typing import Optional

# revision identifiers, used by Alembic.
revision = "0216c880cd8b"
down_revision = "fe51b503d5ed"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "fitbit_subscription_id", sa.Integer, unique=True, autoincrement=True
        ),
    )


def downgrade():
    op.drop_column("users", "fitbit_subscription_id")
