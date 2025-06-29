"""add backup id to server_logs

Revision ID: 6a02208f9a44
Revises: 234e793607b5
Create Date: 2020-12-26 22:15:12.678033

"""

from typing import Optional

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6a02208f9a44"
down_revision = "234e793607b5"
branch_labels: Optional[tuple[str]] = None
depends_on: Optional[str] = None


def upgrade():
    op.add_column("server_logs", sa.Column("backup_id", sa.Integer, nullable=True))
    op.create_foreign_key(
        "server_logs_servers_backup_backup_id",
        "server_logs",
        "server_backups",
        ["backup_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="NO ACTION",
    )


def downgrade():
    op.drop_constraint("server_logs_servers_backup_backup_id", "server_logs")
    op.drop_column("server_logs", "backup_id")
