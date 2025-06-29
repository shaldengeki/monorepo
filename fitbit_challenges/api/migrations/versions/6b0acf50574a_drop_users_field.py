"""drop-users-field

Revision ID: 6b0acf50574a
Revises: c7de6c21bfa9
Create Date: 2023-07-08 19:19:04.935293

"""

import sqlalchemy as sa
from alembic import op
from typing import Optional

# revision identifiers, used by Alembic.
revision = "6b0acf50574a"
down_revision = "c7de6c21bfa9"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.drop_column("challenges", "users")


def downgrade():
    op.add_column(
        "challenges",
        sa.Column("users", sa.Unicode(500), nullable=False),
    )
