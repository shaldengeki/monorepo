"""create-game-statistics-table

Revision ID: deca8621de11
Revises: 142c66849d87
Create Date: 2024-09-21 20:06:15.079991

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.functions import now

# revision identifiers, used by Alembic.
revision = "deca8621de11"
down_revision = "142c66849d87"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "game_statistics",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("bga_table_id", sa.Integer, nullable=False),
        sa.Column("bga_user_id", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, default=now, nullable=False),
        # statistics. see PlayerStats in protobuf.
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("rank", sa.Integer, nullable=False),
        sa.Column("thinking_time", sa.Integer, nullable=False),
        sa.Column("starting_position", sa.Integer, nullable=False),
        sa.Column("turns", sa.Integer, nullable=False),
        sa.Column("breaks_triggered", sa.Integer, nullable=False),
        sa.Column("triggered_end", sa.Boolean, nullable=False),
        sa.Column("map_id", sa.Integer, nullable=False),
        sa.Column("appeal", sa.Integer, nullable=False),
        sa.Column("conservation", sa.Integer, nullable=False),
        sa.Column("reputation", sa.Integer, nullable=False),
        sa.Column("actions_build", sa.Integer, nullable=False),
        sa.Column("actions_animals", sa.Integer, nullable=False),
        sa.Column("actions_cards", sa.Integer, nullable=False),
        sa.Column("actions_association", sa.Integer, nullable=False),
        sa.Column("actions_sponsors", sa.Integer, nullable=False),
        sa.Column("x_tokens_gained", sa.Integer, nullable=False),
        sa.Column("x_actions", sa.Integer, nullable=False),
        sa.Column("x_tokens_used", sa.Integer, nullable=False),
        sa.Column("money_gained", sa.Integer, nullable=False),
        sa.Column("money_gained_through_income", sa.Integer, nullable=False),
        sa.Column("money_spent_on_animals", sa.Integer, nullable=False),
        sa.Column("money_spent_on_enclosures", sa.Integer, nullable=False),
        sa.Column("money_spent_on_donations", sa.Integer, nullable=False),
        sa.Column(
            "money_spent_on_playing_cards_from_reputation_range",
            sa.Integer,
            nullable=False,
        ),
        sa.Column("cards_drawn_from_deck", sa.Integer, nullable=False),
        sa.Column("cards_drawn_from_reputation_range", sa.Integer, nullable=False),
        sa.Column("cards_snapped", sa.Integer, nullable=False),
        sa.Column("cards_discarded", sa.Integer, nullable=False),
        sa.Column("played_sponsors", sa.Integer, nullable=False),
        sa.Column("played_animals", sa.Integer, nullable=False),
        sa.Column("released_animals", sa.Integer, nullable=False),
        sa.Column("association_workers", sa.Integer, nullable=False),
        sa.Column("association_donations", sa.Integer, nullable=False),
        sa.Column("association_reputation_actions", sa.Integer, nullable=False),
        sa.Column("association_partner_zoo_actions", sa.Integer, nullable=False),
        sa.Column("association_university_actions", sa.Integer, nullable=False),
        sa.Column(
            "association_conservation_project_actions", sa.Integer, nullable=False
        ),
        sa.Column("built_enclosures", sa.Integer, nullable=False),
        sa.Column("built_kiosks", sa.Integer, nullable=False),
        sa.Column("built_pavilions", sa.Integer, nullable=False),
        sa.Column("built_unique_buildings", sa.Integer, nullable=False),
        sa.Column("hexes_covered", sa.Integer, nullable=False),
        sa.Column("hexes_empty", sa.Integer, nullable=False),
        sa.Column("upgraded_action_cards", sa.Integer, nullable=False),
        sa.Column("upgraded_animals", sa.Boolean, nullable=False),
        sa.Column("upgraded_build", sa.Boolean, nullable=False),
        sa.Column("upgraded_cards", sa.Boolean, nullable=False),
        sa.Column("upgraded_sponsors", sa.Boolean, nullable=False),
        sa.Column("upgraded_association", sa.Boolean, nullable=False),
        sa.Column("icons_africa", sa.Integer, nullable=False),
        sa.Column("icons_europe", sa.Integer, nullable=False),
        sa.Column("icons_asia", sa.Integer, nullable=False),
        sa.Column("icons_australia", sa.Integer, nullable=False),
        sa.Column("icons_americas", sa.Integer, nullable=False),
        sa.Column("icons_bird", sa.Integer, nullable=False),
        sa.Column("icons_predator", sa.Integer, nullable=False),
        sa.Column("icons_herbivore", sa.Integer, nullable=False),
        sa.Column("icons_bear", sa.Integer, nullable=False),
        sa.Column("icons_reptile", sa.Integer, nullable=False),
        sa.Column("icons_primate", sa.Integer, nullable=False),
        sa.Column("icons_petting_zoo", sa.Integer, nullable=False),
        sa.Column("icons_sea_animal", sa.Integer, nullable=False),
        sa.Column("icons_water", sa.Integer, nullable=False),
        sa.Column("icons_rock", sa.Integer, nullable=False),
        sa.Column("icons_science", sa.Integer, nullable=False),
    )

    op.create_index(
        "game_statistics_bga_table_id",
        "game_statistics",
        ["bga_table_id"],
    )

    op.create_index(
        "game_statistics_user_id",
        "game_statistics",
        ["user_id"],
    )


def downgrade():
    op.drop_index("game_statistics_bga_table_id", "game_statistics")
    op.drop_index("game_statistics_user_id", "game_statistics")
    op.drop_table("game_statistics")
