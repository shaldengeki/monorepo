import datetime
import enum
import json

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from proto_registry.config import db


class Base(DeclarativeBase):
    pass


class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    versions: Mapped["SubjectVersion"] = relationship(
        back_populates="subject", order_by="desc(SubjectVersion.version_id)"
    )

    def __repr__(self):
        return f"<Subject name={self.name}>"


class SchemaType(enum.Enum):
    AVRO = 1
    PROTOBUF = 2
    JSONSCHEMA = 3


subject_version_reference_table = db.Table(
    "subject_version_references",
    db.Column(
        "referrer_id",
        db.Integer,
        db.ForeignKey("subject_versions.id"),
        primary_key=True,
    ),
    db.Column(
        "referred_id",
        db.Integer,
        db.ForeignKey("subject_versions.id"),
        primary_key=True,
    ),
)


class SubjectVersion(Base):
    __tablename__ = "subject_versions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
        nullable=False,
    )
    version_id: Mapped[int] = mapped_column(Integer, nullable=False)
    schema_type: Mapped[SchemaType] = mapped_column(
        Enum(SchemaType), nullable=True, default=SchemaType.AVRO
    )
    schema: Mapped[str] = mapped_column(String, nullable=False)

    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    subject: Mapped["Subject"] = relationship(
        back_populates="versions", order_by="desc(SubjectVersion.version_id)"
    )
    references: Mapped["SubjectVersion"] = relationship(
        "SubjectVersion",
        secondary=subject_version_reference_table,
        primaryjoin=id == subject_version_reference_table.c.referrer_id,
        secondaryjoin=id == subject_version_reference_table.c.referred_id,
        lazy="subquery",
        backref=db.backref("referrers", lazy=True),
    )

    def __repr__(self):
        return f"<SubjectVersion id={self.id}>"

    def unique_name(self):
        return f"{self.subject.name}/{self.version_id}"
