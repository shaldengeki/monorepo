"""populate-challenge-memberships

Revision ID: c7de6c21bfa9
Revises: 441677e6cdf5
Create Date: 2023-07-08 17:06:04.501044

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c7de6c21bfa9"
down_revision = "441677e6cdf5"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            insert into challenge_memberships (challenge_id, fitbit_user_id, created_at)
            select id, unnest(string_to_array(challenges.users, ',')), created_at from challenges
        """
    )


def downgrade():
    op.execute(
        """
            truncate table challenge_memberships
        """
    )
