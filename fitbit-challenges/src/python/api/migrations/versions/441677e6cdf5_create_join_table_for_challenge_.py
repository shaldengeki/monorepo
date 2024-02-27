"""create-join-table-for-challenge-membership

Revision ID: 441677e6cdf5
Revises: d2401a8f7896
Create Date: 2023-07-08 16:08:56.071920

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.functions import now


# revision identifiers, used by Alembic.
revision = "441677e6cdf5"
down_revision = "d2401a8f7896"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "challenge_memberships",
        sa.Column("fitbit_user_id", sa.Unicode(100)),
        sa.Column("challenge_id", sa.Integer, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), default=now, nullable=False
        ),
    )
    op.create_index(
        "challenge_memberships_fitbit_user_id_created_at",
        "challenge_memberships",
        ["fitbit_user_id", "created_at"],
    )
    op.create_index(
        "challenge_memberships_challenge_id_fitbit_user_id",
        "challenge_memberships",
        ["challenge_id", "fitbit_user_id"],
        unique=True,
    )


def downgrade():
    op.drop_index(
        "challenge_memberships_challenge_id_fitbit_user_id", "challenge_memberships"
    )
    op.drop_index(
        "challenge_memberships_fitbit_user_id_created_at", "challenge_memberships"
    )
    op.drop_table("challenge_memberships")
