import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ark_nova_stats.config import db


class GameLog(db.Model):  # type: ignore
    __tablename__ = "game_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    log: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )
    bga_table_id: Mapped[int]

    users: Mapped[list["User"]] = relationship(
        secondary="game_participations", back_populates="game_logs", viewonly=True
    )

    user_participations: Mapped[list["GameParticipation"]] = relationship(
        back_populates="game_log"
    )


class User(db.Model):  # type: ignore
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    bga_id: Mapped[int]
    name: Mapped[str]
    avatar: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )

    game_logs: Mapped[list["GameLog"]] = relationship(
        secondary="game_participations", back_populates="users", viewonly=True
    )
    game_participations: Mapped[list["GameParticipation"]] = relationship(
        back_populates="user"
    )


class GameParticipation(db.Model):  # type: ignore
    __tablename__ = "game_participations"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    game_log_id: Mapped[int] = mapped_column(
        ForeignKey("game_logs.id"), primary_key=True
    )
    color: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="game_participations")
    game_log: Mapped["GameLog"] = relationship(back_populates="user_participations")
