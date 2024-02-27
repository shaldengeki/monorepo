"""create user table

Revision ID: 9632e0e256e7
Revises: 7606b7c4f65f
Create Date: 2023-05-27 16:35:15.474646

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.functions import now


# revision identifiers, used by Alembic.
revision = "9632e0e256e7"
down_revision = "7606b7c4f65f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("fitbit_user_id", sa.Unicode(100), primary_key=True),
        sa.Column("display_name", sa.Unicode(100), nullable=True),
        sa.Column("created_at", sa.DateTime, default=now, nullable=False),
        sa.Column("fitbit_access_token", sa.Unicode(100), nullable=False),
        sa.Column("fitbit_refresh_token", sa.Unicode(100), nullable=False),
        sa.Column("synced_at", sa.DateTime, nullable=True),
    )


def downgrade():
    op.drop_table("users")
