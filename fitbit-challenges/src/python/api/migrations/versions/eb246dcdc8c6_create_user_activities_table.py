"""create user_activities table

Revision ID: eb246dcdc8c6
Revises: fc584ec8e573
Create Date: 2023-04-20 23:15:51.565977

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.functions import now, current_date


# revision identifiers, used by Alembic.
revision = "eb246dcdc8c6"
down_revision = "fc584ec8e573"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_activities",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("created_at", sa.DateTime, default=now, nullable=False),
        sa.Column("updated_at", sa.DateTime, default=now, nullable=False),
        sa.Column("record_date", sa.Date, default=current_date, nullable=False),
        sa.Column("user", sa.Unicode(500), nullable=False),
        sa.Column("steps", sa.Integer, nullable=False),
        sa.Column("active_minutes", sa.Integer, nullable=False),
        sa.Column("distance_km", sa.DECIMAL(5, 2), nullable=False),
    )

    op.create_index(
        "user_activities_user_record_date_created_at",
        "user_activities",
        ["user", "record_date", "created_at"],
    )


def downgrade():
    op.drop_table("user_activities")
