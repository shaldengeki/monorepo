import csv
import datetime
import json
import logging
import os
import tarfile
import tempfile
from typing import Optional

import sqlalchemy
from sqlalchemy import desc

from ark_nova_stats.config import db
from ark_nova_stats.emu_cup.tables import EMU_CUP_GAME_TABLE_IDS
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
        self._filename: Optional[str] = None
        self.archive_tempfile: Optional[tempfile._TemporaryFileWrapper[bytes]] = None
        self.archive_tarfile: Optional[tarfile.TarFile] = None

    @property
    def archive_type(self) -> GameLogArchiveType:
        raise NotImplementedError

    def should_include_game_log(self, game_log: GameLog) -> bool:
        return True

    def process_game_log(self, game_log: GameLog) -> None:
        if not self.should_include_game_log(game_log):
            return

        self.num_logs += 1
        game_users: list[User] = game_log.users
        self.users.update(set([u.name for u in game_users]))
        if self.last_log is None or self.last_log.game_end < game_log.game_end:
            self.last_log = game_log

    @property
    def filename(self) -> str:
        if self._filename is None:
            self._filename = (
                self.archive_type.name
                + "_"
                + datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y_%m_%d")
                + ".tar.gz"
            )

        return self._filename

    def should_create_archive(self) -> bool:
        # First, bail if we've uploaded an archive recently.
        last_archive: Optional[GameLogArchive] = (
            GameLogArchive.query.filter(
                GameLogArchive.archive_type == self.archive_type
            )
            .order_by(desc(GameLogArchive.created_at))
            .first()
        )
        if last_archive is None:
            return True

        time_since_last_archive = datetime.datetime.now() - last_archive.created_at
        if time_since_last_archive < self.min_interval:
            self.logger.debug(
                f"Last archive was uploaded at {last_archive.created_at}, which was {time_since_last_archive} ago; skipping."
            )
            return False

        # Next, check to see if we have new logs to include in the archive.
        new_logs = GameLog.query.where(
            GameLog.id > last_archive.last_game_log_id
        ).count()
        if new_logs == 0:
            self.logger.debug(
                f"No new logs to include since game ID {last_archive.last_game_log_id}; skipping."
            )
            return False

        return True

    def game_logs(self) -> "sqlalchemy.orm.query.Query[GameLog]":
        return GameLog.query.yield_per(10)

    def create_archive_tempfile(self, directory: str) -> tarfile.TarFile:
        self.logger.info(f"Creating archive at: {self.filename}")
        self.archive_tempfile = tempfile.NamedTemporaryFile(
            suffix=self.filename, dir=directory, delete=False
        )
        self.archive_tarfile = tarfile.open(self.archive_tempfile.name, "w:gz")
        return self.archive_tarfile

    def upload_archive(self) -> None:
        # Upload the compressed gzip jsonl to Tigris.
        if self.archive_tarfile is None or self.archive_tempfile is None:
            raise ValueError(
                f"Cannot call upload_archive before we've created the tempfile."
            )

        os.fsync(self.archive_tempfile)
        self.archive_tarfile.close()
        self.archive_tempfile.close()

        key = self.archive_type.name + "/" + self.filename
        size_bytes = os.path.getsize(self.archive_tempfile.name)
        self.tigris_client.upload_file(
            self.archive_tempfile.name,
            os.getenv("BUCKET_NAME"),
            key,
        )
        self.logger.info(f"Uploaded game log archive at: {key} with size: {size_bytes}")

    def record_archive(self) -> GameLogArchive:
        # Record this archive in the database.
        if self.archive_tempfile is None:
            raise ValueError(
                "Cannot call record_archive before we've created the tempfile."
            )

        url = f"{os.getenv('TIGRIS_CUSTOM_DOMAIN_HOST')}/{self.archive_type.name}/{self.filename}"
        size_bytes = os.path.getsize(self.archive_tempfile.name)

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

    def process_game_log(self, game_log: GameLog) -> None:
        if self.archive_tarfile is None or self.archive_tempfile is None:
            raise ValueError(
                "Cannot call process_game_log before creating the archive tarfile."
            )

        super(RawBGALogArchiveCreator, self).process_game_log(game_log)

        user_names = "_".join([u.name.replace(" ", "_") for u in game_log.users])
        log_tempfile_name = f"{game_log.bga_table_id}_{user_names}.json"
        with tempfile.NamedTemporaryFile(
            suffix=log_tempfile_name, mode="w"
        ) as log_tempfile:
            log_tempfile.write(game_log.log)
            log_tempfile.flush()
            os.fsync(log_tempfile)

            self.archive_tarfile.add(log_tempfile.name, arcname=log_tempfile_name)
            os.fsync(self.archive_tempfile)


class BGAWithELOArchiveCreator(GameLogArchiveCreator):
    @property
    def archive_type(self) -> GameLogArchiveType:
        return GameLogArchiveType.BGA_JSONL_WITH_ELO

    def process_game_log(self, game_log: GameLog) -> None:
        if self.archive_tarfile is None or self.archive_tempfile is None:
            raise ValueError(
                "Cannot call process_game_log before creating the archive tarfile."
            )

        super(BGAWithELOArchiveCreator, self).process_game_log(game_log)

        user_names = "_".join([u.name.replace(" ", "_") for u in game_log.users])

        ratings = game_log.game_ratings
        payload = {}
        if ratings is not None:
            payload["elos"] = {
                rating.user_id: {
                    "prior_elo": rating.prior_elo,
                    "new_elo": rating.new_elo,
                    "prior_arena_elo": rating.prior_arena_elo,
                    "new_arena_elo": rating.new_arena_elo,
                }
                for rating in ratings
            }
        if game_log.game_statistics is not None:
            payload["statistics"] = {
                stat.bga_user_id: {
                    "score": stat.score,
                    "rank": stat.rank,
                    "thinking_time": stat.thinking_time,
                    "starting_position": stat.starting_position,
                    "turns": stat.turns,
                    "breaks_triggered": stat.breaks_triggered,
                    "triggered_end": stat.triggered_end,
                    "map_id": stat.map_id,
                    "appeal": stat.appeal,
                    "conservation": stat.conservation,
                    "reputation": stat.reputation,
                    "actions_build": stat.actions_build,
                    "actions_animals": stat.actions_animals,
                    "actions_cards": stat.actions_cards,
                    "actions_association": stat.actions_association,
                    "actions_sponsors": stat.actions_sponsors,
                    "x_tokens_gained": stat.x_tokens_gained,
                    "x_actions": stat.x_actions,
                    "x_tokens_used": stat.x_tokens_used,
                    "money_gained": stat.money_gained,
                    "money_gained_through_income": stat.money_gained_through_income,
                    "money_spent_on_animals": stat.money_spent_on_animals,
                    "money_spent_on_enclosures": stat.money_spent_on_enclosures,
                    "money_spent_on_donations": stat.money_spent_on_donations,
                    "money_spent_on_playing_cards_from_reputation_range": stat.money_spent_on_playing_cards_from_reputation_range,
                    "cards_drawn_from_deck": stat.cards_drawn_from_deck,
                    "cards_drawn_from_reputation_range": stat.cards_drawn_from_reputation_range,
                    "cards_snapped": stat.cards_snapped,
                    "cards_discarded": stat.cards_discarded,
                    "played_sponsors": stat.played_sponsors,
                    "played_animals": stat.played_animals,
                    "released_animals": stat.released_animals,
                    "association_workers": stat.association_workers,
                    "association_donations": stat.association_donations,
                    "association_reputation_actions": stat.association_reputation_actions,
                    "association_partner_zoo_actions": stat.association_partner_zoo_actions,
                    "association_university_actions": stat.association_university_actions,
                    "association_conservation_project_actions": stat.association_conservation_project_actions,
                    "built_enclosures": stat.built_enclosures,
                    "built_kiosks": stat.built_kiosks,
                    "built_pavilions": stat.built_pavilions,
                    "built_unique_buildings": stat.built_unique_buildings,
                    "hexes_covered": stat.hexes_covered,
                    "hexes_empty": stat.hexes_empty,
                    "upgraded_action_cards": stat.upgraded_action_cards,
                    "upgraded_animals": stat.upgraded_animals,
                    "upgraded_build": stat.upgraded_build,
                    "upgraded_cards": stat.upgraded_cards,
                    "upgraded_sponsors": stat.upgraded_sponsors,
                    "upgraded_association": stat.upgraded_association,
                    "icons_africa": stat.icons_africa,
                    "icons_europe": stat.icons_europe,
                    "icons_asia": stat.icons_asia,
                    "icons_australia": stat.icons_australia,
                    "icons_americas": stat.icons_americas,
                    "icons_bird": stat.icons_bird,
                    "icons_predator": stat.icons_predator,
                    "icons_herbivore": stat.icons_herbivore,
                    "icons_bear": stat.icons_bear,
                    "icons_reptile": stat.icons_reptile,
                    "icons_primate": stat.icons_primate,
                    "icons_petting_zoo": stat.icons_petting_zoo,
                    "icons_sea_animal": stat.icons_sea_animal,
                    "icons_water": stat.icons_water,
                    "icons_rock": stat.icons_rock,
                    "icons_science": stat.icons_science,
                }
                for stat in game_log.game_statistics
            }

        log_tempfile_name = f"{game_log.bga_table_id}_{user_names}.json"
        with tempfile.NamedTemporaryFile(
            suffix=log_tempfile_name, mode="w"
        ) as log_tempfile:
            payload["log"] = json.loads(game_log.log)
            log_tempfile.write(json.dumps(payload))
            log_tempfile.flush()
            os.fsync(log_tempfile)

            self.archive_tarfile.add(log_tempfile.name, arcname=log_tempfile_name)
            os.fsync(self.archive_tempfile)


class TopLevelStatsCsvArchiveCreator(GameLogArchiveCreator):
    def __init__(self, *args, **kwargs) -> None:
        super(TopLevelStatsCsvArchiveCreator, self).__init__(*args, **kwargs)
        self.csv_filename = self.filename.replace(".tar.gz", ".csv")
        self.csv_file = tempfile.NamedTemporaryFile(suffix=self.csv_filename, mode="w")
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=self.csv_field_names)
        self.csv_writer.writeheader()

    @property
    def archive_type(self) -> GameLogArchiveType:
        return GameLogArchiveType.TOP_LEVEL_STATS_CSV

    @property
    def csv_field_names(self) -> list[str]:
        return [
            "bga_table_id",
            "user_id",
            "prior_elo",
            "new_elo",
            "prior_arena_elo",
            "new_arena_elo",
            "score",
            "rank",
            "thinking_time",
            "starting_position",
            "turns",
            "breaks_triggered",
            "triggered_end",
            "map_id",
            "appeal",
            "conservation",
            "reputation",
            "actions_build",
            "actions_animals",
            "actions_cards",
            "actions_association",
            "actions_sponsors",
            "x_tokens_gained",
            "x_actions",
            "x_tokens_used",
            "money_gained",
            "money_gained_through_income",
            "money_spent_on_animals",
            "money_spent_on_enclosures",
            "money_spent_on_donations",
            "money_spent_on_playing_cards_from_reputation_range",
            "cards_drawn_from_deck",
            "cards_drawn_from_reputation_range",
            "cards_snapped",
            "cards_discarded",
            "played_sponsors",
            "played_animals",
            "released_animals",
            "association_workers",
            "association_donations",
            "association_reputation_actions",
            "association_partner_zoo_actions",
            "association_university_actions",
            "association_conservation_project_actions",
            "built_enclosures",
            "built_kiosks",
            "built_pavilions",
            "built_unique_buildings",
            "hexes_covered",
            "hexes_empty",
            "upgraded_action_cards",
            "upgraded_animals",
            "upgraded_build",
            "upgraded_cards",
            "upgraded_sponsors",
            "upgraded_association",
            "icons_africa",
            "icons_europe",
            "icons_asia",
            "icons_australia",
            "icons_americas",
            "icons_bird",
            "icons_predator",
            "icons_herbivore",
            "icons_bear",
            "icons_reptile",
            "icons_primate",
            "icons_petting_zoo",
            "icons_sea_animal",
            "icons_water",
            "icons_rock",
            "icons_science",
        ]

    def process_game_log(self, game_log: GameLog) -> None:
        super(TopLevelStatsCsvArchiveCreator, self).process_game_log(game_log)
        if not self.should_include_game_log(game_log):
            return

        rows: list[dict] = []
        for user in game_log.users:
            row = {k: None for k in self.csv_field_names}
            row["bga_table_id"] = game_log.bga_table_id
            row["user_id"] = user.bga_id

            for rating in game_log.game_ratings:
                if rating.user_id == user.bga_id:
                    row.update(
                        {
                            "prior_elo": rating.prior_elo,
                            "new_elo": rating.new_elo,
                            "prior_arena_elo": rating.prior_arena_elo,
                            "new_arena_elo": rating.new_arena_elo,
                        }
                    )
                    break

            for stat in game_log.game_statistics:
                if stat.bga_user_id == user.bga_id:
                    row.update(
                        {
                            "score": stat.score,
                            "rank": stat.rank,
                            "thinking_time": stat.thinking_time,
                            "starting_position": stat.starting_position,
                            "turns": stat.turns,
                            "breaks_triggered": stat.breaks_triggered,
                            "triggered_end": stat.triggered_end,
                            "map_id": stat.map_id,
                            "appeal": stat.appeal,
                            "conservation": stat.conservation,
                            "reputation": stat.reputation,
                            "actions_build": stat.actions_build,
                            "actions_animals": stat.actions_animals,
                            "actions_cards": stat.actions_cards,
                            "actions_association": stat.actions_association,
                            "actions_sponsors": stat.actions_sponsors,
                            "x_tokens_gained": stat.x_tokens_gained,
                            "x_actions": stat.x_actions,
                            "x_tokens_used": stat.x_tokens_used,
                            "money_gained": stat.money_gained,
                            "money_gained_through_income": stat.money_gained_through_income,
                            "money_spent_on_animals": stat.money_spent_on_animals,
                            "money_spent_on_enclosures": stat.money_spent_on_enclosures,
                            "money_spent_on_donations": stat.money_spent_on_donations,
                            "money_spent_on_playing_cards_from_reputation_range": stat.money_spent_on_playing_cards_from_reputation_range,
                            "cards_drawn_from_deck": stat.cards_drawn_from_deck,
                            "cards_drawn_from_reputation_range": stat.cards_drawn_from_reputation_range,
                            "cards_snapped": stat.cards_snapped,
                            "cards_discarded": stat.cards_discarded,
                            "played_sponsors": stat.played_sponsors,
                            "played_animals": stat.played_animals,
                            "released_animals": stat.released_animals,
                            "association_workers": stat.association_workers,
                            "association_donations": stat.association_donations,
                            "association_reputation_actions": stat.association_reputation_actions,
                            "association_partner_zoo_actions": stat.association_partner_zoo_actions,
                            "association_university_actions": stat.association_university_actions,
                            "association_conservation_project_actions": stat.association_conservation_project_actions,
                            "built_enclosures": stat.built_enclosures,
                            "built_kiosks": stat.built_kiosks,
                            "built_pavilions": stat.built_pavilions,
                            "built_unique_buildings": stat.built_unique_buildings,
                            "hexes_covered": stat.hexes_covered,
                            "hexes_empty": stat.hexes_empty,
                            "upgraded_action_cards": stat.upgraded_action_cards,
                            "upgraded_animals": stat.upgraded_animals,
                            "upgraded_build": stat.upgraded_build,
                            "upgraded_cards": stat.upgraded_cards,
                            "upgraded_sponsors": stat.upgraded_sponsors,
                            "upgraded_association": stat.upgraded_association,
                            "icons_africa": stat.icons_africa,
                            "icons_europe": stat.icons_europe,
                            "icons_asia": stat.icons_asia,
                            "icons_australia": stat.icons_australia,
                            "icons_americas": stat.icons_americas,
                            "icons_bird": stat.icons_bird,
                            "icons_predator": stat.icons_predator,
                            "icons_herbivore": stat.icons_herbivore,
                            "icons_bear": stat.icons_bear,
                            "icons_reptile": stat.icons_reptile,
                            "icons_primate": stat.icons_primate,
                            "icons_petting_zoo": stat.icons_petting_zoo,
                            "icons_sea_animal": stat.icons_sea_animal,
                            "icons_water": stat.icons_water,
                            "icons_rock": stat.icons_rock,
                            "icons_science": stat.icons_science,
                        }
                    )
                    break

            rows.append(row)

        if not rows:
            return

        for row in rows:
            self.csv_writer.writerow(row)

    def upload_archive(self) -> None:
        if self.archive_tarfile is None or self.archive_tempfile is None:
            raise ValueError(
                "Cannot call upload_archive before creating the archive tarfile."
            )

        self.csv_file.flush()
        self.archive_tarfile.add(self.csv_file.name, arcname=self.csv_filename)
        os.fsync(self.archive_tempfile)
        super(TopLevelStatsCsvArchiveCreator, self).upload_archive()
        self.csv_file.close()


class EmuCupTopLevelStatsCsvArchiveCreator(TopLevelStatsCsvArchiveCreator):
    @property
    def archive_type(self) -> GameLogArchiveType:
        return GameLogArchiveType.EMU_CUP_TOP_LEVEL_STATS_CSV

    def game_logs(self) -> "sqlalchemy.orm.query.Query[GameLog]":
        return GameLog.query.where(
            GameLog.bga_table_id.in_(EMU_CUP_GAME_TABLE_IDS)
        ).yield_per(10)

    def should_include_game_log(self, game_log: GameLog) -> bool:
        if not super().should_include_game_log(game_log):
            return False

        return bool(game_log.bga_table_id in EMU_CUP_GAME_TABLE_IDS)
