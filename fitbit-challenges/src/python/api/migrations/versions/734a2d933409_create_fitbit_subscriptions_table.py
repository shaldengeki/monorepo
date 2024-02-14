"""create fitbit_subscriptions table

Revision ID: 734a2d933409
Revises: 647568a75ffe
Create Date: 2023-06-05 21:57:44.334780

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "734a2d933409"
down_revision = "647568a75ffe"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "fitbit_subscriptions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("fitbit_user_id", sa.Unicode(100), nullable=False),
    )
    op.create_index(
        "fitbit_subscriptions_fitbit_user_id",
        "fitbit_subscriptions",
        columns=["fitbit_user_id"],
        unique=True,
    )


def downgrade():
    op.drop_index("fitbit_subscriptions_fitbit_user_id", "fitbit_subscriptions")
    op.drop_table("fitbit_subscriptions")
