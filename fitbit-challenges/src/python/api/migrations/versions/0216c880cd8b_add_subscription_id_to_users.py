"""add subscription_id to users

Revision ID: 0216c880cd8b
Revises: fe51b503d5ed
Create Date: 2023-05-28 16:22:44.511833

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0216c880cd8b"
down_revision = "fe51b503d5ed"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "fitbit_subscription_id", sa.Integer, unique=True, autoincrement=True
        ),
    )


def downgrade():
    op.drop_column("users", "fitbit_subscription_id")
