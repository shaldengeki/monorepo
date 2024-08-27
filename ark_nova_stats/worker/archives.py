import datetime
import json
import logging
import os
import tarfile
import tempfile
from typing import Optional

from sqlalchemy import desc

from ark_nova_stats.config import db
from ark_nova_stats.models import GameLog, GameLogArchive, GameLogArchiveType, User


class GameLogArchiveCreator:
    def __init__(
        self, logger: logging.Logger, tigris_client, min_interval: datetime.timedelta
    ):
        self.logger = logger
        self.tigris_client = tigris_client
        self.min_interval = min_interval
        self.num_logs = 0
        self.users: set[str] = set()
        self.last_log: Optional[GameLog] = None

    @property
    def archive_type(self) -> GameLogArchiveType:
        raise NotImplementedError

    def process_game_log(
        self, game_log: GameLog, archive_tarfile: tarfile.TarFile
    ) -> GameLog:
        raise NotImplementedError

    def filename(self) -> str:
        return (
            self.archive_type.name
            + "_"
            + datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y_%m_%d")
            + ".tar.gz"
        )

    def create_archive(self) -> Optional[GameLogArchive]:
        # First, bail if we've uploaded an archive recently.
        last_archive: GameLogArchive = GameLogArchive.query.order_by(
            desc(GameLogArchive.created_at)
        ).first()
        if last_archive is not None:
            time_since_last_archive = datetime.datetime.now() - last_archive.created_at
            if time_since_last_archive < self.min_interval:
                self.logger.debug(
                    f"Last archive was uploaded at {last_archive.created_at}, which was {time_since_last_archive} ago; skipping."
                )
                return None

            # Next, check to see if we have new logs to include in the archive.
            new_logs = GameLog.query.where(
                GameLog.id > last_archive.last_game_log_id
            ).count()
            if new_logs == 0:
                self.logger.debug(
                    f"No new logs to include since game ID {last_archive.last_game_log_id}; skipping."
                )
                return None

        filename = self.filename()
        self.logger.info(f"Creating archive at: {filename}")

        # For each batch, write a logfile.
        with tempfile.NamedTemporaryFile(suffix=filename) as archive_tempfile:
            with tarfile.open(archive_tempfile.name, "w:gz") as archive_tarfile:
                for game_log in GameLog.query.yield_per(10):
                    self.process_game_log(game_log, archive_tarfile)
                    self.num_logs += 1
                    game_users: list[User] = game_log.users
                    self.users.update(set([u.name for u in game_users]))
                    if (
                        self.last_log is None
                        or self.last_log.created_at < game_log.created_at
                    ):
                        self.last_log = game_log

            # Upload the compressed gzip jsonl to Tigris.
            self.tigris_client.upload_file(
                archive_tempfile.name,
                os.getenv("BUCKET_NAME"),
                self.archive_type.name + "/" + filename,
            )
            url = f"{os.getenv('TIGRIS_CUSTOM_DOMAIN_HOST')}/{self.archive_type.name}/{filename}"
            size_bytes = os.path.getsize(archive_tempfile.name)

        self.logger.info(f"Uploaded game log archive at: {url} with size: {size_bytes}")

        # Record this archive in the database.
        if self.last_log is None:
            last_game_log_id = None
        else:
            last_game_log_id = self.last_log.id

        new_archive = GameLogArchive(
            url=url,
            archive_type=self.archive_type.value,
            size_bytes=size_bytes,
            num_game_logs=self.num_logs,
            num_users=len(self.users),
            last_game_log_id=last_game_log_id,
        )

        db.session.add(new_archive)
        db.session.commit()
        self.logger.info(
            f"Recorded a new game log archive at: {url} with {self.num_logs} games"
        )

        return new_archive


class RawBGALogArchiveCreator(GameLogArchiveCreator):
    @property
    def archive_type(self) -> GameLogArchiveType:
        return GameLogArchiveType.RAW_BGA_JSONL

    def process_game_log(self, game_log: GameLog, archive_tarfile: tarfile.TarFile):
        user_names = "_".join([u.name.replace(" ", "_") for u in game_log.users])
        log_tempfile_name = f"{game_log.bga_table_id}_{user_names}.json"
        with tempfile.NamedTemporaryFile(
            suffix=log_tempfile_name, mode="w"
        ) as log_tempfile:
            log_tempfile.write(game_log.log)
            log_tempfile.flush()
            os.fsync(log_tempfile)

            archive_tarfile.add(log_tempfile.name, arcname=log_tempfile_name)


class BGAWithELOArchiveCreator(GameLogArchiveCreator):
    def __init__(self, *args, **kwargs):
        super(BGAWithELOArchiveCreator, self).__init__(*args, **kwargs)
        self.user_bga_id_to_name = self.initialize_users()

    @property
    def archive_type(self) -> GameLogArchiveType:
        return GameLogArchiveType.BGA_JSONL_WITH_ELO

    def initialize_users(self) -> dict[int, str]:
        return {user.bga_id: user.name for user in User.query.all()}

    def process_game_log(self, game_log: GameLog, archive_tarfile: tarfile.TarFile):
        user_names = "_".join([u.name.replace(" ", "_") for u in game_log.users])

        ratings = game_log.game_ratings
        payload = {}
        if ratings is not None:
            payload["elos"] = {
                self.user_bga_id_to_name[rating.user_id]: {
                    "prior_elo": rating.prior_elo,
                    "new_elo": rating.new_elo,
                    "prior_arena_elo": rating.prior_arena_elo,
                    "new_arena_elo": rating.new_arena_elo,
                }
                for rating in ratings
            }

        log_tempfile_name = f"{game_log.bga_table_id}_{user_names}.json"
        with tempfile.NamedTemporaryFile(
            suffix=log_tempfile_name, mode="w"
        ) as log_tempfile:
            payload["log"] = json.loads(game_log.log)
            log_tempfile.write(json.dumps(payload))
            log_tempfile.flush()
            os.fsync(log_tempfile)

            archive_tarfile.add(log_tempfile.name, arcname=log_tempfile_name)
