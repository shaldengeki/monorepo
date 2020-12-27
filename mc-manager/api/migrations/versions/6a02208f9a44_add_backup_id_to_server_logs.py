"""add backup id to server_logs

Revision ID: 6a02208f9a44
Revises: 234e793607b5
Create Date: 2020-12-26 22:15:12.678033

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6a02208f9a44"
down_revision = "234e793607b5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("server_logs", sa.Column("backup_id", sa.Integer, nullable=True))
    op.create_foreign_key(
        "server_logs_servers_backup_backup_id",
        "server_logs",
        "server_backups",
        ["backup_id"],
        ["id"],
        "CASCADE",
        "NO ACTION",
    )


def downgrade():
    op.drop_constraint("server_logs_servers_backup_backup_id", "server_logs")
    op.drop_column("server_logs", "backup_id")
