"""alter fitbit subscription type to text

Revision ID: 647568a75ffe
Revises: a7c2b36b742b
Create Date: 2023-05-29 21:51:31.670121

"""

from typing import Optional

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "647568a75ffe"
down_revision = "a7c2b36b742b"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.alter_column(
        "users",
        "fitbit_subscription_id",
        type_=sa.Unicode(50),
        existing_type=sa.Integer,
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "users",
        "fitbit_subscription_id",
        type_=sa.Integer,
        existing_type=sa.Unicode(50),
        existing_nullable=False,
    )
