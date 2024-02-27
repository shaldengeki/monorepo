"""drop-users-field

Revision ID: 6b0acf50574a
Revises: c7de6c21bfa9
Create Date: 2023-07-08 19:19:04.935293

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6b0acf50574a"
down_revision = "c7de6c21bfa9"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("challenges", "users")


def downgrade():
    op.add_column(
        "challenges",
        sa.Column("users", sa.Unicode(500), nullable=False),
    )
