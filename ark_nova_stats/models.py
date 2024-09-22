import datetime
import enum
from typing import Generator, Optional

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
    game_start: Mapped[datetime.datetime]
    game_end: Mapped[datetime.datetime]

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

    game_ratings: Mapped[list["GameRating"]] = relationship(back_populates="game_log")

    game_statistics: Mapped[list["GameStatistics"]] = relationship(
        back_populates="game_log"
    )

    def create_related_objects(
        self, parsed_logs: ParsedGameLog
    ) -> Generator[db.Model, None, None]:
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
            user = bga_id_to_user[bga_user.id]
            yield GameParticipation(
                user=user,
                color=log_user.color,
                game_log=self,
            )

        for c in self.create_card_and_plays(parsed_logs):
            yield c

        for s in self.create_game_statistics(parsed_logs):
            yield s

    def create_card_and_plays(
        self, parsed_logs: ParsedGameLog
    ) -> Generator[db.Model, None, None]:
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

    def create_game_statistics(
        self, parsed_logs: ParsedGameLog
    ) -> Generator[db.Model, None, None]:
        for s in parsed_logs.parse_game_stats().player_stats:
            yield GameStatistics(
                bga_table_id=parsed_logs.table_id,
                bga_user_id=s.player_id,
                score=s.score,
                rank=s.rank,
                thinking_time=s.thinking_time,
                starting_position=s.starting_position,
                turns=s.turns,
                breaks_triggered=s.breaks_triggered,
                triggered_end=s.triggered_end,
                map_id=s.map_id,
                appeal=s.appeal,
                conservation=s.conservation,
                reputation=s.reputation,
                actions_build=s.actions_build,
                actions_animals=s.actions_animals,
                actions_cards=s.actions_cards,
                actions_association=s.actions_association,
                actions_sponsors=s.actions_sponsors,
                x_tokens_gained=s.x_tokens_gained,
                x_actions=s.x_actions,
                x_tokens_used=s.x_tokens_used,
                money_gained=s.money_gained,
                money_gained_through_income=s.money_gained_through_income,
                money_spent_on_animals=s.money_spent_on_animals,
                money_spent_on_enclosures=s.money_spent_on_enclosures,
                money_spent_on_donations=s.money_spent_on_donations,
                money_spent_on_playing_cards_from_reputation_range=s.money_spent_on_playing_cards_from_reputation_range,
                money_spent_on_playing_cards_from_reputation_range=s.money_spent_on_playing_cards_from_reputation_range,
                cards_drawn_from_deck=s.cards_drawn_from_deck,
                cards_drawn_from_reputation_range=s.cards_drawn_from_reputation_range,
                cards_snapped=s.cards_snapped,
                cards_discarded=s.cards_discarded,
                played_sponsors=s.played_sponsors,
                played_animals=s.played_animals,
                release_animals=s.release_animals,
                association_workers=s.association_workers,
                association_donations=s.association_donations,
                association_reputation_actions=s.association_reputation_actions,
                association_partner_zoo_actions=s.association_partner_zoo_actions,
                association_university_actions=s.association_university_actions,
                association_conservation_project_actions=s.association_conservation_project_actions,
                built_enclosures=s.built_enclosures,
                built_kiosks=s.built_kiosks,
                built_pavilions=s.built_pavilions,
                built_unique_buildings=s.built_unique_buildings,
                hexes_covered=s.hexes_covered,
                hexes_empty=s.hexes_empty,
                upgraded_action_cards=s.upgraded_action_cards,
                upgraded_animals=s.upgraded_animals,
                upgraded_build=s.upgraded_build,
                upgraded_cards=s.upgraded_cards,
                upgraded_sponsors=s.upgraded_sponsors,
                upgraded_association=s.upgraded_association,
                icons_africa=s.icons_africa,
                icons_europe=s.icons_europe,
                icons_asia=s.icons_asia,
                icons_australia=s.icons_australia,
                icons_americas=s.icons_americas,
                icons_bird=s.icons_bird,
                icons_predator=s.icons_predator,
                icons_herbivore=s.icons_herbivore,
                icons_bear=s.icons_bear,
                icons_reptile=s.icons_reptile,
                icons_primate=s.icons_primate,
                icons_petting_zoo=s.icons_petting_zoo,
                icons_sea_animal=s.icons_sea_animal,
                icons_water=s.icons_water,
                icons_rock=s.icons_rock,
                icons_science=s.icons_science,
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
        secondary="game_participations",
        back_populates="users",
        viewonly=True,
    )
    game_participations: Mapped[list["GameParticipation"]] = relationship(
        back_populates="user"
    )
    card_plays: Mapped[list["CardPlay"]] = relationship(back_populates="user")

    cards: Mapped[list["Card"]] = relationship(
        secondary="game_log_cards", back_populates="users", viewonly=True
    )
    game_ratings: Mapped[list["GameRating"]] = relationship(back_populates="user")
    game_statistics: Mapped[list["GameStatistics"]] = relationship(
        back_populates="user"
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
            .join(GameLog, GameLog.id == GameParticipation.game_log_id)
            .order_by(desc(GameLog.game_end))
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

    def latest_game(self) -> Select[tuple["GameLog"]]:
        return (
            select(GameLog)
            .join(GameRating, GameRating.bga_table_id == GameLog.bga_table_id)
            .where(GameRating.user_id == self.bga_id)
            .order_by(desc(GameLog.game_end))
            .limit(1)
        )

    def current_elo(self) -> Optional[int]:
        latest_rating: Optional[GameRating] = (
            GameRating.query.join(
                GameLog, GameLog.bga_table_id == GameRating.bga_table_id
            )
            .where(GameRating.user_id == self.id)
            .where(GameRating.new_elo != None)
            .order_by(desc(GameLog.game_end))
            .limit(1)
            .first()
        )

        if latest_rating is None:
            return None

        return latest_rating.new_elo

    def current_arena_elo(self) -> Optional[int]:
        latest_rating: Optional[GameRating] = (
            GameRating.query.join(
                GameLog, GameLog.bga_table_id == GameRating.bga_table_id
            )
            .where(GameRating.user_id == self.id)
            .where(GameRating.new_arena_elo != None)
            .order_by(desc(GameLog.game_end))
            .limit(1)
            .first()
        )

        if latest_rating is None:
            return None

        return latest_rating.new_arena_elo


class GameLogArchiveType(enum.IntEnum):
    GAME_LOG_ARCHIVE_TYPE_UNKNOWN = 0
    RAW_BGA_JSONL = 1
    BGA_JSONL_WITH_ELO = 2
    TOP_LEVEL_STATS_CSV = 3


class GameLogArchive(db.Model):
    __tablename__ = "game_log_archives"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    archive_type: Mapped[int]
    url: Mapped[str]
    size_bytes: Mapped[int]
    num_game_logs: Mapped[int]
    num_users: Mapped[int]
    last_game_log_id: Mapped[int] = mapped_column(ForeignKey("game_logs.id"))
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
            .join(GameLog, GameLog.id == CardPlay.game_log_id)
            .where(CardPlay.card_id == self.id)
            .order_by(desc(GameLog.game_end))
            .limit(num)
        )

    def recent_game_logs(self, num=10) -> Select[tuple["GameLog"]]:
        return (
            select(GameLog)
            .join(CardPlay, CardPlay.game_log_id == GameLog.id)
            .where(CardPlay.card_id == self.id)
            .order_by(desc(GameLog.game_end))
            .limit(num)
        )

    def recent_users(self, num=10) -> Select[tuple["User"]]:
        return (
            select(User)
            .join(CardPlay, CardPlay.user_id == User.bga_id)
            .join(GameLog, GameLog.id == CardPlay.game_log_id)
            .where(CardPlay.card_id == self.id)
            .order_by(desc(GameLog.game_end))
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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_log_id: Mapped[int] = mapped_column(ForeignKey("game_logs.id"))
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.bga_id"))
    move: Mapped[int]
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="card_plays")
    game_log: Mapped["GameLog"] = relationship(back_populates="card_plays")
    card: Mapped["Card"] = relationship(back_populates="plays")


class GameRating(db.Model):
    __tablename__ = "game_ratings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bga_table_id: Mapped[int] = mapped_column(ForeignKey("game_logs.bga_table_id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.bga_id"))
    prior_elo: Mapped[Optional[int]]
    new_elo: Mapped[Optional[int]]
    prior_arena_elo: Mapped[Optional[int]]
    new_arena_elo: Mapped[Optional[int]]
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="game_ratings")
    game_log: Mapped["GameLog"] = relationship(back_populates="game_ratings")


class GameStatistics(db.Model):
    __tablename__ = "game_statistics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bga_table_id: Mapped[int] = mapped_column(ForeignKey("game_logs.bga_table_id"))
    bga_user_id: Mapped[int] = mapped_column(ForeignKey("users.bga_id"))
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )

    score: Mapped[int]
    rank: Mapped[int]
    thinking_time: Mapped[int]
    starting_position: Mapped[int]
    turns: Mapped[int]
    breaks_triggered: Mapped[int]
    triggered_end: Mapped[int]
    map_id: Mapped[int]
    appeal: Mapped[int]
    conservation: Mapped[int]
    reputation: Mapped[int]
    actions_build: Mapped[int]
    actions_animals: Mapped[int]
    actions_cards: Mapped[int]
    actions_association: Mapped[int]
    actions_sponsors: Mapped[int]
    x_tokens_gained: Mapped[int]
    x_actions: Mapped[int]
    x_tokens_used: Mapped[int]
    money_gained: Mapped[int]
    money_gained_through_income: Mapped[int]
    money_spent_on_animals: Mapped[int]
    money_spent_on_enclosures: Mapped[int]
    money_spent_on_donations: Mapped[int]
    money_spent_on_playing_cards_from_reputation_range: Mapped[int]
    cards_drawn_from_deck: Mapped[int]
    cards_drawn_from_reputation_range: Mapped[int]
    cards_snapped: Mapped[int]
    cards_discarded: Mapped[int]
    played_sponsors: Mapped[int]
    played_animals: Mapped[int]
    release_animals: Mapped[int]
    association_workers: Mapped[int]
    association_donations: Mapped[int]
    association_reputation_actions: Mapped[int]
    association_partner_zoo_actions: Mapped[int]
    association_university_actions: Mapped[int]
    association_conservation_project_actions: Mapped[int]
    built_enclosures: Mapped[int]
    built_kiosks: Mapped[int]
    built_pavilions: Mapped[int]
    built_unique_buildings: Mapped[int]
    hexes_covered: Mapped[int]
    hexes_empty: Mapped[int]
    upgraded_action_cards: Mapped[bool]
    upgraded_animals: Mapped[bool]
    upgraded_build: Mapped[bool]
    upgraded_cards: Mapped[bool]
    upgraded_sponsors: Mapped[bool]
    upgraded_association: Mapped[bool]
    icons_africa: Mapped[int]
    icons_europe: Mapped[int]
    icons_asia: Mapped[int]
    icons_australia: Mapped[int]
    icons_americas: Mapped[int]
    icons_bird: Mapped[int]
    icons_predator: Mapped[int]
    icons_herbivore: Mapped[int]
    icons_bear: Mapped[int]
    icons_reptile: Mapped[int]
    icons_primate: Mapped[int]
    icons_petting_zoo: Mapped[int]
    icons_sea_animal: Mapped[int]
    icons_water: Mapped[int]
    icons_rock: Mapped[int]
    icons_science: Mapped[int]

    user: Mapped["User"] = relationship(back_populates="game_statistics")
    game_log: Mapped["GameLog"] = relationship(back_populates="game_statistics")
