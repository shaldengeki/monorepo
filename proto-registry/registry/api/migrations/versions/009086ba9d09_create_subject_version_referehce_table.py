"""create subject_version_referehce table

Revision ID: 009086ba9d09
Revises: 86ac1c2d94b4
Create Date: 2022-07-28 02:17:55.026039

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "009086ba9d09"
down_revision = "86ac1c2d94b4"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "subject_version_references",
        sa.Column("referrer_id", sa.Integer),
        sa.Column("referred_id", sa.Integer),
    )
    op.create_unique_constraint(
        "subject_version_references_referrer_referred",
        "subject_version_references",
        ["referrer_id", "referred_id"],
    )
    op.create_foreign_key(
        "subject_version_references_subject_versions_referrer_id",
        "subject_version_references",
        "subject_versions",
        ["referrer_id"],
        ["id"],
        "CASCADE",
        "CASCADE",
    )
    op.create_foreign_key(
        "subject_version_references_subject_versions_referred_id",
        "subject_version_references",
        "subject_versions",
        ["referred_id"],
        ["id"],
        "CASCADE",
        "CASCADE",
    )
    op.create_index(
        "subject_version_references_index_referrer_referred",
        "subject_version_references",
        ["referrer_id", "referred_id"],
        unique=True,
    )
    op.create_index(
        "subject_version_references_index_referred_referrer",
        "subject_version_references",
        ["referred_id", "referrer_id"],
        unique=True,
    )


def downgrade():
    op.drop_table("subject_version_references")
