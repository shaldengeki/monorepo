"""create subscription notification table

Revision ID: 7606b7c4f65f
Revises: 62e12d1c75ae
Create Date: 2023-05-25 00:27:12.752830

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.functions import now


# revision identifiers, used by Alembic.
revision = "7606b7c4f65f"
down_revision = "62e12d1c75ae"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "subscription_notifications",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("created_at", sa.DateTime, default=now, nullable=False),
        sa.Column("processed_at", sa.DateTime, nullable=True),
        sa.Column("collection_type", sa.Unicode(100), nullable=False),
        sa.Column("date", sa.DateTime, nullable=False),
        sa.Column("fitbit_user_id", sa.Unicode(100), nullable=False),
    )

    op.create_index(
        "subscription_notifications_processed_at",
        "subscription_notifications",
        ["processed_at"],
    )


def downgrade():
    op.drop_table("subscription_notifications")
