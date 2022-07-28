"""create subject_versions table

Revision ID: 86ac1c2d94b4
Revises: 9da1de15cd6a
Create Date: 2022-07-21 04:39:32.310089

"""
from alembic import op
import datetime
import enum
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "86ac1c2d94b4"
down_revision = "9da1de15cd6a"
branch_labels = None
depends_on = None


class SchemaType(enum.Enum):
    AVRO = 1
    PROTOBUF = 2
    JSONSCHEMA = 3


def upgrade():
    op.create_table(
        "subject_versions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "created", sa.DateTime, nullable=False, default=datetime.datetime.utcnow
        ),
        sa.Column("version_id", sa.Integer, nullable=False),
        sa.Column("subject_id", sa.Integer, nullable=False),
        sa.Column(
            "schema_type", sa.Enum(SchemaType), nullable=False, default=SchemaType.AVRO
        ),
        sa.Column("schema", sa.Unicode(20000), nullable=False),
    )
    op.create_unique_constraint(
        "subject_versions_version_id", "subject_versions", ["subject_id", "version_id"]
    )
    op.create_foreign_key(
        "subject_versions_subjects_subject_id",
        "subject_versions",
        "subjects",
        ["subject_id"],
        ["id"],
        "CASCADE",
        "CASCADE",
    )
    op.create_index(
        "subject_versions_subject_id",
        "subject_versions",
        ["subject_id", "version_id"],
    )


def downgrade():
    op.drop_table("subject_versions")
