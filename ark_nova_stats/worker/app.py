import datetime
import logging
import os
import time

import boto3
from sqlalchemy import desc

from ark_nova_stats.config import app, db
from ark_nova_stats.models import GameLog, GameLogArchive

max_delay = 10

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s] %(message)s", level=logging.WARNING
)
logger = logging.getLogger(__name__)


def archive_logs_to_tigris(tigris_client) -> None:
    # First, bail if we've uploaded an archive recently.
    UPLOAD_ARCHIVE_ONCE_EVERY = datetime.timedelta(days=1)

    last_archive: GameLogArchive = GameLogArchive.query.order_by(
        desc(GameLogArchive.created_at)
    ).first()
    time_since_last_archive = datetime.datetime.now() - last_archive.created_at
    if last_archive is not None and time_since_last_archive < UPLOAD_ARCHIVE_ONCE_EVERY:
        logger.debug(
            f"Last archive was uploaded at {last_archive.created_at}, which was {time_since_last_archive} ago; skipping."
        )
        return

    # First, retrieve all the game logs so we can serialize them.
    for game_log in GameLog.query.all():
        # TODO: serialize game_log to CSV, then use tigris_client.upload_fileobj()
        pass


def main() -> int:
    tigris_client = boto3.client("s3", endpoint_url=os.getenv("AWS_ENDPOINT_URL_S3"))
    with app.app_context():
        while True:
            start = time.time()
            # Do work here.
            archive_logs_to_tigris(tigris_client)
            delay = (start + max_delay) - time.time()
            if delay > 0:
                time.sleep(delay)


if __name__ == "__main__":
    raise SystemExit(main())
