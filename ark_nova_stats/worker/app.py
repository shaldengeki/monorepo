import datetime
import gzip
import io
import logging
import os
import tarfile
import tempfile
import time
from typing import Iterator, Optional

import boto3
from sqlalchemy import desc

from ark_nova_stats.config import app, db
from ark_nova_stats.models import GameLog, GameLogArchive, GameLogArchiveType, User

max_delay = 12 * 60 * 60

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def archive_logs_to_tigris(
    tigris_client, min_interval: datetime.timedelta = datetime.timedelta(days=1)
) -> Optional[GameLogArchive]:
    # TODO: convert all of these database requests to GraphQL requests over the internal network.

    # First, bail if we've uploaded an archive recently.
    last_archive: GameLogArchive = GameLogArchive.query.order_by(
        desc(GameLogArchive.created_at)
    ).first()
    if last_archive is not None:
        time_since_last_archive = datetime.datetime.now() - last_archive.created_at
        if time_since_last_archive < min_interval:
            logger.debug(
                f"Last archive was uploaded at {last_archive.created_at}, which was {time_since_last_archive} ago; skipping."
            )
            return None

        # Next, check to see if we have new logs to include in the archive.
        new_logs = GameLog.query.where(
            GameLog.id > last_archive.last_game_log_id
        ).count()
        if new_logs == 0:
            logger.debug(
                f"No new logs to include since game ID {last_archive.last_game_log_id}; skipping."
            )
            return None

    # Retrieve all the game logs so we can serialize them.
    all_logs: Iterator[GameLog] = GameLog.query.yield_per(10)  # type: ignore
    num_game_logs = 0
    users: set[str] = set()
    last_game_log: Optional[GameLog] = None
    archive_type = GameLogArchiveType.RAW_BGA_JSONL
    filename = (
        archive_type.name
        + "_"
        + datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y_%m_%d")
        + ".tar.gz"
    )

    # For each batch, write a logfile.
    with tempfile.NamedTemporaryFile(suffix=filename) as archive_tempfile:
        with tarfile.open(archive_tempfile.name, "w:gz") as archive_tarfile:
            for game_log in all_logs:
                num_game_logs += 1
                user_names = "_".join([u.name for u in game_log.users])
                log_tempfile_name = f"{game_log.bga_table_id}_{user_names}.json"
                with tempfile.NamedTemporaryFile(
                    suffix=log_tempfile_name, mode="w"
                ) as log_tempfile:
                    log_tempfile.write(game_log.log)
                    log_tempfile.flush()
                    os.fsync(log_tempfile)

                    archive_tarfile.add(log_tempfile.name, arcname=log_tempfile_name)

                game_users: list[User] = game_log.users
                users.update(set([u.name for u in game_users]))
                if (
                    last_game_log is None
                    or last_game_log.created_at < game_log.created_at
                ):
                    last_game_log = game_log

        # Upload the compressed gzip jsonl to Tigris.
        tigris_client.upload_file(
            archive_tempfile.name,
            os.getenv("BUCKET_NAME"),
            archive_type.name + "/" + filename,
        )
        url = f"{os.getenv('TIGRIS_CUSTOM_DOMAIN_HOST')}/{archive_type.name}/{filename}"
        size_bytes = os.path.getsize(archive_tempfile.name)

    logger.info(f"Uploaded game log archive at: {url} with size: {size_bytes}")

    # Record this archive in the database.
    if last_game_log is None:
        last_game_log_id = None
    else:
        last_game_log_id = last_game_log.id

    new_archive = GameLogArchive(
        url=url,
        archive_type=archive_type.value,
        size_bytes=size_bytes,
        num_game_logs=num_game_logs,
        num_users=len(users),
        last_game_log_id=last_game_log_id,
    )

    db.session.add(new_archive)
    db.session.commit()
    logger.info(f"Recorded a new game log archive at: {url} with {num_game_logs} games")
    return new_archive


API_SECRET_KEY = os.getenv("API_WORKER_SECRET")


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
