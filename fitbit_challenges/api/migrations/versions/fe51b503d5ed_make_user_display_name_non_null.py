"""make user display name non-null

Revision ID: fe51b503d5ed
Revises: d1f9f7da8cdb
Create Date: 2023-05-28 02:38:49.087217

"""

from typing import Optional

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fe51b503d5ed"
down_revision = "d1f9f7da8cdb"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.alter_column("users", "display_name", nullable=False)


def downgrade():
    op.alter_column("users", "display_name", nullable=True)
