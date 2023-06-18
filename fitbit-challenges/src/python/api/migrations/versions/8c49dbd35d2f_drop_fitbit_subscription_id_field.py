"""drop fitbit_subscription_id field

Revision ID: 8c49dbd35d2f
Revises: 6f3be7b63455
Create Date: 2023-06-06 02:34:47.766633

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8c49dbd35d2f"
down_revision = "6f3be7b63455"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("users", "fitbit_subscription_id")


def downgrade():
    op.add_column(
        "users",
        sa.Column(
            "fitbit_subscription_id", sa.Unicode(50), unique=True, autoincrement=True
        ),
    )

    op.execute(
        """
        update users
        set fitbit_subscription_id = (
            select id from fitbit_subscriptions
            where fitbit_subscriptions.fitbit_user_id = users.fitbit_user_id
        )
        where exists (
            select * from fitbit_subscriptions
            where fitbit_subscriptions.fitbit_user_id = users.fitbit_user_id
        )
        """
    )
