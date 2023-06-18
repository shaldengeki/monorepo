"""populate fitbit_subscriptions

Revision ID: 6f3be7b63455
Revises: 734a2d933409
Create Date: 2023-06-06 02:27:44.569918

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "6f3be7b63455"
down_revision = "734a2d933409"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            insert into fitbit_subscriptions (id, fitbit_user_id)
            select cast(fitbit_subscription_id as integer), fitbit_user_id
            from users
            where fitbit_subscription_id IS NOT NULL
                and fitbit_subscription_id != 'None'
        """
    )


def downgrade():
    op.execute(
        """
            truncate table fitbit_subscriptions
        """
    )
