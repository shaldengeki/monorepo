import datetime
import json
import logging
import os
import tempfile
import time
from typing import Optional

import boto3

from ark_nova_stats.bga_log_parser.game_log import GameLog as BGAGameLog
from ark_nova_stats.config import app, db
from ark_nova_stats.models import (
    Card,
    CardPlay,
    GameLog,
    GameLogArchive,
    GameStatistics,
)
from ark_nova_stats.worker.archives import (
    BGAWithELOArchiveCreator,
    EmuCupTopLevelStatsCsvArchiveCreator,
    TopLevelStatsCsvArchiveCreator,
)

max_delay = 12 * 60 * 60

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def archive_logs_to_tigris(
    tigris_client, min_interval: datetime.timedelta = datetime.timedelta(days=1)
) -> list[GameLogArchive]:
    archives = []
    archive_types = [
        archive_type(
            logger=logger,
            tigris_client=tigris_client,
            min_interval=min_interval,
        )
        for archive_type in (
            BGAWithELOArchiveCreator,
            TopLevelStatsCsvArchiveCreator,
            EmuCupTopLevelStatsCsvArchiveCreator,
        )
    ]
    archive_types_to_create = [
        archive_type
        for archive_type in archive_types
        if archive_type.should_create_archive()
    ]

    if not archive_types_to_create:
        return []

    logger.info(
        f"Creating archives for types: {[str(t.archive_type) for t in archive_types_to_create]}"
    )
    logs_processed = 0

    with tempfile.TemporaryDirectory() as tmpdirname:
        for archive_type in archive_types_to_create:
            archive_type.create_archive_tempfile(tmpdirname)

        for game_log in archive_types_to_create[0].game_logs():
            logs_processed += 1
            for archive_type in archive_types_to_create:
                archive_type.process_game_log(game_log)

            if logs_processed % 100 == 0:
                logger.info(f"Processed {logs_processed} game logs for archive...")

        for archive_type in archive_types_to_create:
            archive_type.upload_archive()
            archives.append(archive_type.record_archive())

    return archives


def populate_card_play_actions() -> None:
    logger.info(f"Populating card play actions.")
    card_ids = set()
    for game_log in db.session.execute(db.select(GameLog)).yield_per(10):
        parsed_log = BGAGameLog(**json.loads(game_log.log))
        # First, create underlying card models.
        for play in parsed_log.data.card_plays:
            # Check to see if it exists.
            if play.card.id in card_ids:
                continue

            find_card = db.session.execute(
                db.select(Card).where(Card.bga_id == play.card.id).count()
            ).scalar_one()
            if find_card > 0:
                card_ids.add(play.card.id)
                continue

            card = Card(name=play.card.name, bga_id=play.card.id)
            logger.info(f"Staging card creation for: {play.card.id}")
            db.session.add(card)
            card_ids.add(play.card.id)

    logger.info("Committing all the new cards.")
    db.session.commit()

    # Now create all the card plays.
    logging.info("Creating card plays.")
    for game_log in db.session.execute(db.select(GameLog)).yield_per(10):
        parsed_log = BGAGameLog(**json.loads(game_log.log))
        for play in parsed_log.data.card_plays:
            find_play = db.session.execute(
                db.select(CardPlay)
                .where(
                    CardPlay.game_log_id == game_log.id
                    and CardPlay.card_id == play.card.id
                    and CardPlay.user_id == play.player.id
                    and CardPlay.move == play.move
                )
                .count()
            ).scalar_one()
            if find_play > 0:
                continue

            card = db.session.execute(
                db.select(Card).where(Card.bga_id == play.card.id).limit(1)
            ).scalar_one()
            logger.info(
                f"Staging card play creation for game ID {game_log.id}, card {play.card.id}"
            )

            db.session.add(
                CardPlay(
                    game_log_id=game_log.id,
                    card=card,
                    user_id=play.player.id,
                    move=play.move,
                )
            )

    logger.info("Committing all the new card plays.")
    db.session.commit()

    logger.info("Done creating new card plays!")


def populate_game_log_start_end() -> None:
    logger.info(f"Populating game log start & ends.")
    updated = 0
    for game_log in db.session.execute(
        db.select(GameLog).where(GameLog.game_start == None).limit(25)
    ).yield_per(10):
        parsed_log = BGAGameLog(**json.loads(game_log.log))
        game_log.game_start = parsed_log.game_start
        game_log.game_end = parsed_log.game_end
        updated += 1

    logger.info("Committing all the populated game log starts & ends.")
    db.session.commit()
    logger.info(f"Done populating {updated} game log starts & ends!")


def populate_game_statistics() -> None:
    logger.info(f"Populating game statistics.")
    updated = 0
    for game_log in db.session.execute(
        db.select(GameLog)
        .outerjoin(GameStatistics)
        .where(GameStatistics.bga_table_id == None)
        .limit(25)
    ).yield_per(10):
        parsed_log = BGAGameLog(**json.loads(game_log.log))
        for s in game_log.create_game_statistics(parsed_log):
            db.session.add(s)
        updated += 1

    logger.info(f"Committing {updated} populated game statistics.")
    db.session.commit()
    logger.info(f"Done populating {updated} game statistics!")


API_SECRET_KEY = os.getenv("API_WORKER_SECRET")


def main() -> int:
    tigris_client = boto3.client("s3", endpoint_url=os.getenv("AWS_ENDPOINT_URL_S3"))  # type: ignore
    with app.app_context():
        while True:
            start = time.time()
            # Do work here.
            archive_logs_to_tigris(tigris_client)
            # populate_card_play_actions()
            # populate_game_log_start_end()
            # populate_game_statistics()
            delay = (start + max_delay) - time.time()
            if delay > 0:
                time.sleep(delay)


if __name__ == "__main__":
    raise SystemExit(main())
