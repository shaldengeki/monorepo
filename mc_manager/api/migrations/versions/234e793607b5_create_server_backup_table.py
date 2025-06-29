"""create server backup table

Revision ID: 234e793607b5
Revises: 4d81354c3a36
Create Date: 2020-12-24 14:50:28.952014

"""

import datetime
from typing import Optional

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "234e793607b5"
down_revision = "4d81354c3a36"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.create_table(
        "server_backups",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("server_id", sa.Integer, nullable=False),
        sa.Column(
            "created", sa.DateTime, nullable=False, default=datetime.datetime.utcnow
        ),
        sa.Column("state", sa.Unicode(100), nullable=False),
        sa.Column("error", sa.Unicode(500)),
        sa.Column("remote_path", sa.Unicode(500), nullable=True),
    )
    op.create_unique_constraint(
        "server_backups_remote_path", "server_backups", ["remote_path"]
    )
    op.create_foreign_key(
        "server_backups_servers_server_id",
        "server_backups",
        "servers",
        ["server_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_index(
        "server_backups_server_id",
        "server_backups",
        ["server_id", "created"],
    )


def downgrade():
    op.drop_table("server_backups")
