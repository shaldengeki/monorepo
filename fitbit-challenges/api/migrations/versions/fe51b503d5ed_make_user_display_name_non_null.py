"""make user display name non-null

Revision ID: fe51b503d5ed
Revises: d1f9f7da8cdb
Create Date: 2023-05-28 02:38:49.087217

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fe51b503d5ed"
down_revision = "d1f9f7da8cdb"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("users", "display_name", nullable=False)


def downgrade():
    op.alter_column("users", "display_name", nullable=True)
