import datetime
import json
import logging
import os
import tempfile
import time

import boto3

from ark_nova_stats.bga_log_parser.game_log import GameLog as BGAGameLog
from ark_nova_stats.config import app, db
from ark_nova_stats.models import Card, CardPlay, GameLog, GameLogArchive
from ark_nova_stats.worker.archives import (
    BGAWithELOArchiveCreator,
    RawBGALogArchiveCreator,
)

max_delay = 60

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def archive_logs_to_tigris(
    tigris_client, min_interval: datetime.timedelta = datetime.timedelta(days=1)
) -> list[GameLogArchive]:
    # TODO: convert all of these database requests to GraphQL requests over the internal network.
    archives = []
    archive_types = [
        archive_type(
            logger=logger,
            tigris_client=tigris_client,
            min_interval=min_interval,
        )
        for archive_type in (RawBGALogArchiveCreator, BGAWithELOArchiveCreator)
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

    for game_log in GameLog.query.yield_per(10):  # type: ignore
        parsed_log = BGAGameLog(**json.loads(game_log.log))
        # First, create underlying card models.
        for play in parsed_log.data.card_plays:
            # Check to see if it exists.
            if play.card.id in card_ids:
                continue

            find_card = Card.query.where(Card.bga_id == play.card.id).count()
            if find_card > 0:
                card_ids.add(play.card.id)
                continue

            card = Card(name=play.card.name, bga_id=play.card.id)  # type: ignore
            logger.info(f"Staging card creation for: {play.card.id}")
            db.session.add(card)
            card_ids.add(play.card.id)

    logger.info("Committing all the new cards.")
    db.session.commit()

    # Now create all the card plays.
    logging.info("Creating card plays.")
    for log_model in GameLog.query.yield_per(10):  # type: ignore
        parsed_log = BGAGameLog(**json.loads(log_model.log))
        for play in parsed_log.data.card_plays:
            find_play = CardPlay.query.where(
                CardPlay.game_log_id == log_model.id
                and CardPlay.card_id == card.id
                and CardPlay.user_id == play.player.id
                and CardPlay.move == play.move
            ).count()
            if find_play > 0:
                continue

            find_card = Card.query.where(Card.bga_id == play.card.id).limit(1).all()
            card = find_card[0]
            logger.info(
                f"Staging card play creation for game ID {log_model.id}, card {card.id}"
            )

            db.session.add(
                CardPlay(  # type: ignore
                    game_log_id=log_model.id,
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
    for game_log in GameLog.query.where(GameLog.game_start is None).limit(100).yield_per(10):  # type: ignore
        parsed_log = BGAGameLog(**json.loads(game_log.log))
        game_log.game_start = parsed_log.game_start
        game_log.game_end = parsed_log.game_end
        updated += 1

    logger.info("Committing all the populated game log starts & ends.")
    db.session.commit()
    logger.info(f"Done populating {updated} game log starts & ends!")


API_SECRET_KEY = os.getenv("API_WORKER_SECRET")


def main() -> int:
    tigris_client = boto3.client("s3", endpoint_url=os.getenv("AWS_ENDPOINT_URL_S3"))
    with app.app_context():
        while True:
            start = time.time()
            # Do work here.
            archive_logs_to_tigris(tigris_client)
            # populate_card_play_actions()
            populate_game_log_start_end()
            delay = (start + max_delay) - time.time()
            if delay > 0:
                time.sleep(delay)


if __name__ == "__main__":
    raise SystemExit(main())
