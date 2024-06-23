"""create transactions table

Revision ID: e683a9926450
Revises: 
Create Date: 2019-10-24 16:01:01.603106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e683a9926450"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("date", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("description", sa.Unicode(500), nullable=False),
        sa.Column("original_description", sa.Unicode(500), nullable=False),
        sa.Column("amount", sa.Integer, nullable=False),
        sa.Column("type", sa.Unicode(100), nullable=False),
        sa.Column("category", sa.Unicode(100), nullable=False),
        sa.Column("account", sa.Unicode(100), nullable=False),
        sa.Column("labels", sa.Unicode(500), nullable=True),
        sa.Column("notes", sa.Unicode(500), nullable=True),
    )
    op.create_index(
        "date_category_account", "transactions", ["date", "category", "account"]
    )


def downgrade():
    op.drop_table("transactions")
