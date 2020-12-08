"""create server logs table

Revision ID: 4d81354c3a36
Revises: 9d3e78009e2e
Create Date: 2020-12-08 12:09:39.612244

"""
from alembic import op
import sqlalchemy as sa
import datetime


# revision identifiers, used by Alembic.
revision = "4d81354c3a36"
down_revision = "9d3e78009e2e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "server_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("server_id", sa.Integer, nullable=False),
        sa.Column(
            "created", sa.DateTime, nullable=False, default=datetime.datetime.utcnow
        ),
        sa.Column("state", sa.Unicode(100), nullable=False),
        sa.Column("error", sa.Unicode(500)),
    )
    op.create_foreign_key(
        "server_logs_servers_server_id",
        "server_logs",
        "servers",
        ["server_id"],
        ["id"],
        "CASCADE",
        "CASCADE",
    )
    op.create_index(
        "server_logs_server_id",
        "server_logs",
        ["server_id", "created"],
    )


def downgrade():
    op.drop_table("server_logs")
