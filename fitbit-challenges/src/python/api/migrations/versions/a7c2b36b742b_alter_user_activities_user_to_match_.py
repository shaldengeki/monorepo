"""alter user_activities user to match user fitbit_user_id

Revision ID: a7c2b36b742b
Revises: 0216c880cd8b
Create Date: 2023-05-29 18:43:33.818274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a7c2b36b742b"
down_revision = "0216c880cd8b"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "user_activities",
        "user",
        type_=sa.Unicode(100),
        existing_type=sa.Unicode(500),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "user_activities",
        "user",
        type_=sa.Unicode(500),
        existing_type=sa.Unicode(100),
        existing_nullable=False,
    )
