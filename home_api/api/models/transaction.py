import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from home_api.config import db


class Base(DeclarativeBase):
    pass


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
        nullable=False,
    )
    description: Mapped[str]
    original_description: Mapped[str]
    amount: Mapped[int]
    type: Mapped[str]
    category: Mapped[str]
    account: Mapped[str]
    labels: Mapped[str]
    notes: Mapped[str]

    def __repr__(self):
        return "<Transaction {id}>".format(id=self.id)
