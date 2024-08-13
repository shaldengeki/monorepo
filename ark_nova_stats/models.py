import datetime
import enum

from sqlalchemy import ForeignKey, Select, desc, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ark_nova_stats.bga_log_parser.game_log import GameLog as ParsedGameLog
from ark_nova_stats.config import db


class GameParticipation(db.Model):
    __tablename__ = "game_participations"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.bga_id"), primary_key=True)
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


class GameLog(db.Model):
    __tablename__ = "game_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
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

    archives: Mapped[list["GameLogArchive"]] = relationship(
        back_populates="last_game_log",
    )

    cards: Mapped[list["Card"]] = relationship(
        secondary="game_log_cards", back_populates="game_logs", viewonly=True
    )

    card_plays: Mapped[list["CardPlay"]] = relationship(back_populates="game_log")

    def create_related_objects(self, parsed_logs: ParsedGameLog) -> db.Model:
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
            bga_id_to_user[user.id] = User(
                bga_id=user.id,
                name=user.name,
                avatar=user.avatar,
            )
            yield bga_id_to_user[user.id]

        # Now create a game participation for each user.
        for bga_user in parsed_logs.data.players:
            log_user = next(u for u in parsed_logs.data.players if u.id == bga_user.id)
            yield GameParticipation(
                user=bga_id_to_user[bga_user.id],
                color=log_user.color,
                game_log=self,
            )

        for c in self.create_card_and_plays(parsed_logs):
            yield c

    def create_card_and_plays(self, parsed_logs: ParsedGameLog) -> db.Model:
        cards = {}
        # Now create a card & card play.
        for play in parsed_logs.data.card_plays:
            if play.card.id not in cards:
                # Check to see if it exists.
                find_card = Card.query.where(Card.bga_id == play.card.id).limit(1).all()
                if not find_card:
                    card = Card(name=play.card.name, bga_id=play.card.id)
                    yield card
                else:
                    card = find_card[0]

                cards[card.bga_id] = card

            yield CardPlay(
                game_log=self,
                card=cards[play.card.id],
                user_id=play.player.id,
                move=play.move,
            )


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
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
    card_plays: Mapped[list["CardPlay"]] = relationship(back_populates="user")

    cards: Mapped[list["Card"]] = relationship(
        secondary="game_log_cards", back_populates="users", viewonly=True
    )

    @property
    def num_game_logs(self) -> int:
        return GameParticipation.query.where(
            GameParticipation.user_id == self.bga_id
        ).count()

    @property
    def recent_game_logs(self) -> list["GameLog"]:
        return [
            p.game_log
            for p in GameParticipation.query.where(
                GameParticipation.user_id == self.bga_id
            )
            .order_by(desc(GameParticipation.game_log_id))
            .limit(10)
            .all()
        ]

    def commonly_played_cards(self, num=10) -> Select[tuple["Card", int]]:
        return (
            select(Card, func.count())
            .join(CardPlay, CardPlay.card_id == Card.id)
            .where(CardPlay.user_id == self.bga_id)
            .group_by(Card)
            .order_by(desc(func.count()))
            .limit(num)
        )


class GameLogArchiveType(enum.IntEnum):
    GAME_LOG_ARCHIVE_TYPE_UNKNOWN = 0
    RAW_BGA_JSONL = 1


class GameLogArchive(db.Model):
    __tablename__ = "game_log_archives"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    archive_type: Mapped[int]
    url: Mapped[str]
    size_bytes: Mapped[int]
    num_game_logs: Mapped[int]
    num_users: Mapped[int]
    last_game_log_id: Mapped[int] = mapped_column(
        ForeignKey("game_logs.id"), primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )

    last_game_log: Mapped[GameLog] = relationship(back_populates="archives")


class Card(db.Model):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    bga_id: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )

    plays: Mapped[list["CardPlay"]] = relationship(back_populates="card")

    game_logs: Mapped[list["GameLog"]] = relationship(
        secondary="game_log_cards", back_populates="cards", viewonly=True
    )

    users: Mapped[list["User"]] = relationship(
        secondary="game_log_cards", back_populates="cards", viewonly=True
    )

    def recent_plays(self, num=10) -> Select[tuple["CardPlay"]]:
        return (
            select(CardPlay)
            .where(CardPlay.card_id == self.id)
            .order_by(desc(CardPlay.game_log_id))
            .limit(num)
        )

    def recent_game_logs(self, num=10) -> Select[tuple["GameLog"]]:
        return (
            select(GameLog)
            .join(CardPlay, CardPlay.game_log_id == GameLog.id)
            .where(CardPlay.card_id == self.id)
            .order_by(desc(CardPlay.game_log_id))
            .limit(num)
        )

    def recent_users(self, num=10) -> Select[tuple["User"]]:
        return (
            select(User)
            .join(CardPlay, CardPlay.user_id == User.bga_id)
            .where(CardPlay.card_id == self.id)
            .order_by(desc(CardPlay.game_log_id))
            .limit(num)
        )

    def most_played_by(self, num=10) -> Select[tuple["User", int]]:
        return (
            select(User, func.count())
            .join(CardPlay, CardPlay.user_id == User.bga_id)
            .where(CardPlay.card_id == self.id)
            .group_by(User)
            .order_by(desc(func.count()))
            .limit(num)
        )


class CardPlay(db.Model):
    __tablename__ = "game_log_cards"

    game_log_id: Mapped[int] = mapped_column(
        ForeignKey("game_logs.id"), primary_key=True
    )
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.bga_id"), primary_key=True)
    move: Mapped[int]
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="card_plays")
    game_log: Mapped["GameLog"] = relationship(back_populates="card_plays")
    card: Mapped["Card"] = relationship(back_populates="plays")
