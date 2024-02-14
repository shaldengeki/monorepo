"""extend fitbit access token

Revision ID: d1f9f7da8cdb
Revises: 9632e0e256e7
Create Date: 2023-05-27 23:51:20.764017

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d1f9f7da8cdb"
down_revision = "9632e0e256e7"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("users", "fitbit_access_token")
    op.add_column(
        "users", sa.Column("fitbit_access_token", sa.Unicode(500), nullable=False)
    )


def downgrade():
    op.drop_column("users", "fitbit_access_token")
    op.add_column(
        "users", sa.Column("fitbit_access_token", sa.Unicode(100), nullable=False)
    )
