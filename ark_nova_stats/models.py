import datetime
import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ark_nova_stats.bga_log_parser.game_log import GameLog as ParsedGameLog
from ark_nova_stats.config import db


class GameParticipation(db.Model):  # type: ignore
    __tablename__ = "game_participations"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.bga_id"), primary_key=True)
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

    def create_related_objects(self, parsed_logs: ParsedGameLog) -> db.Model:  # type: ignore
        # Add users if not present.
        present_users = User.query.filter(
            User.bga_id.in_([user.id for user in parsed_logs.data.players])
        ).all()
        bga_id_to_user = {present.bga_id: present for present in present_users}
        present_user_ids = set(present.bga_id for present in present_users)

        users_to_create = [
            user for user in parsed_logs.data.players if user.id not in present_user_ids
        ]

        for user in users_to_create:
            bga_id_to_user[user.id] = User(  # type: ignore
                bga_id=user.id,
                name=user.name,
                avatar=user.avatar,
            )
            yield bga_id_to_user[user.id]

        # Now create a game participation for each user.
        for bga_user in parsed_logs.data.players:
            log_user = next(u for u in parsed_logs.data.players if u.id == bga_user.id)
            yield GameParticipation(  # type: ignore
                user=bga_id_to_user[bga_user.id],
                color=log_user.color,
                game_log=self,
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


class GameLogArchiveType(enum.Enum):
    GAME_LOG_ARCHIVE_TYPE_UNKNOWN = 0
    RAW_BGA_JSONL = 1


class GameLogArchive(db.Model):  # type: ignore
    id: Mapped[int] = mapped_column(primary_key=True)
    archive_type: Mapped[GameLogArchiveType] = mapped_column(
        default=GameLogArchiveType.GAME_LOG_ARCHIVE_TYPE_UNKNOWN
    )
    url: Mapped[str]
    size_bytes: Mapped[int]
    num_game_logs: Mapped[int]
    num_users: Mapped[int]
    last_game_log_id: Mapped[int] = mapped_column(db.INTEGER, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )
