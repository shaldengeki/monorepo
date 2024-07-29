"""create-user-table

Revision ID: bd2396f61798
Revises: 8c749a7279e7
Create Date: 2024-07-28 22:38:48.238351

"""

import json
import logging

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm
from sqlalchemy.sql.functions import now

from ark_nova_stats.bga_log_parser.game_log import GameLog as BGAGameLog
from ark_nova_stats.models import GameLog as GameLogModel
from ark_nova_stats.models import GameParticipation as GameParticipationModel
from ark_nova_stats.models import User as UserModel

# revision identifiers, used by Alembic.
revision = "bd2396f61798"
down_revision = "8c749a7279e7"
branch_labels = None
depends_on = None


def upgrade():
    # First, create the table & indexes.
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("bga_id", sa.Integer, unique=True),
        sa.Column("name", sa.UnicodeText, nullable=False, unique=True),
        sa.Column("avatar", sa.UnicodeText, nullable=False),
        sa.Column("created_at", sa.DateTime, default=now, nullable=False),
    )

    op.create_index(
        "users_bga_id",
        "users",
        ["bga_id"],
        unique=True,
    )

    op.create_index(
        "users_name",
        "users",
        ["name"],
        unique=True,
    )

    op.create_table(
        "game_participations",
        sa.Column("game_log_id", sa.Integer, nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("color", sa.UnicodeText, nullable=False),
        sa.Column("created_at", sa.DateTime, default=now, nullable=False),
    )

    op.create_index(
        "game_participations_user_id_game_log_id",
        "game_participations",
        ["user_id", "game_log_id"],
        unique=True,
    )

    op.create_index(
        "game_participations_game_log_id",
        "game_participations",
        ["game_log_id"],
    )

    # Next, process game logs and add users.
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    players = {}

    for log_model in session.query(GameLogModel):
        parsed_log = BGAGameLog(**json.loads(log_model.log))
        for player in parsed_log.data.players:
            if player.id not in players:
                players[player.id] = UserModel(  # type: ignore
                    bga_id=player.id, name=player.name, avatar=player.avatar
                )
                session.add(players[player.id])

            session.add(
                GameParticipationModel(  # type: ignore
                    user=players[player.id],
                    color=player.color,
                    game_log_id=parsed_log.data.logs[0].table_id,
                )
            )

    session.commit()


def downgrade():
    op.drop_index("game_participations_game_log_id", "game_participations")
    op.drop_index("game_participations_user_id_game_log_id", "game_participations")
    op.drop_table("game_participations")

    op.drop_index("users_name", "users")
    op.drop_index("users_bga_id", "users")
    op.drop_table("users")
