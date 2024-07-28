"""populate-bga-table-id

Revision ID: b9b6b214018c
Revises: 8c749a7279e7
Create Date: 2024-07-27 20:09:52.563850

"""

import json
import logging

from alembic import op
from sqlalchemy import orm

from ark_nova_stats.bga_log_parser.game_log import GameLog as BGAGameLog
from ark_nova_stats.models import GameLog as GameLogModel

# revision identifiers, used by Alembic.
revision = "b9b6b214018c"
down_revision = "8c749a7279e7"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    logging.info("Processing pre-existing logs.")
    for log_model in session.query(GameLogModel).all():
        logging.info(f"Processing log: {log_model.id}")
        parsed_log = BGAGameLog(**json.loads(log_model.log))
        table_ids = set(l.table_id for l in parsed_log.data.logs)
        if len(table_ids) != 1:
            raise RuntimeError(
                f"Log {log_model.id} is invalid: there must be exactly one table_id per game log, found: {table_ids}"
            )

        log_model.bga_table_id = list(table_ids)[0]

    session.commit()


def downgrade():
    pass
