"""create-bingo-card-

Revision ID: 9dafaf879435
Revises: fc6c9240b3b4
Create Date: 2023-06-18 23:17:42.852140

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.functions import now


# revision identifiers, used by Alembic.
revision = "9dafaf879435"
down_revision = "fc6c9240b3b4"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "bingo_cards",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("fitbit_user_id", sa.Unicode(100), nullable=False),
        sa.Column("challenge_id", sa.Integer, nullable=False),
        sa.Column("rows", sa.Integer, nullable=False),
        sa.Column("columns", sa.Integer, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), default=now, nullable=False
        ),
    )
    op.create_index(
        "bingo_cards_challenge_id_fitbit_user_id",
        "bingo_cards",
        columns=["challenge_id", "fitbit_user_id"],
        unique=True,
    )


def downgrade():
    op.drop_index("bingo_cards_challenge_id_fitbit_user_id", "bingo_cards")
    op.drop_table("bingo_cards")
