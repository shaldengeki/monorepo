"""create server logs table

Revision ID: 4d81354c3a36
Revises: 9d3e78009e2e
Create Date: 2020-12-08 12:09:39.612244

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4d81354c3a36"
down_revision = "9d3e78009e2e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "server_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("created", sa.DateTime, nullable=False),
        sa.Column("state", sa.Unicode(100), nullable=False),
        sa.Column("error", sa.Unicode(500)),
    )


def downgrade():
    op.drop_table("server_logs")
