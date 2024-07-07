#!/usr/bin/env python3

import argparse
import dataclasses
import json
import logging

import qbittorrentapi
import requests

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TorrentInfo:
    torrent_name: str
    category: str
    tags: list[str]
    content_path: str
    root_path: str
    save_path: str
    num_files: int
    torrent_size: int
    current_tracker: str
    info_hash_v1: str
    info_hash_v2: str
    torrent_id: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--torrent-name", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--tags", default="")
    parser.add_argument("--content-path", required=True)
    parser.add_argument("--root-path", required=True)
    parser.add_argument("--save-path", required=True)
    parser.add_argument("--num-files", required=True)
    parser.add_argument("--torrent-size", required=True)
    parser.add_argument("--current-tracker", required=True)
    parser.add_argument("--info-hash-v1", required=True)
    parser.add_argument("--info-hash-v2", required=True)
    parser.add_argument("--torrent-id", required=True)
    parser.add_argument("--log-file", required=True)
    parser.add_argument("--notify-url")
    parser.add_argument("--pause", action="store_true")
    return parser.parse_args()


def write_log(torrent_info: TorrentInfo):
    logger.info(
        f"Received completed torrent: {json.dumps(dataclasses.asdict(torrent_info))}"
    )


def notify_consumer(notify_url: str, torrent_info: TorrentInfo) -> None:
    logger.info(
        f"Notifying consumer at {notify_url} for torrent {torrent_info.torrent_id}"
    )
    requests.post(notify_url, data=dataclasses.asdict(torrent_info))


def pause_torrent(torrent_id: str) -> None:
    logger.info(f"Pausing torrent {torrent_id}")
    with qbittorrentapi.Client(host="localhost", port=8080) as client:
        try:
            client.torrents_pause([torrent_id])
        except qbittorrentapi.NotFound404Error:
            pass


def main() -> int:
    args = parse_args()
    logging.basicConfig(filename=args.log_file, encoding="utf-8", level=logging.INFO)

    if args.tags == "":
        tags = []
    else:
        tags = args.tags.split(",")

    torrent_info = TorrentInfo(
        torrent_name=args.torrent_name,
        category=args.category,
        tags=tags,
        content_path=args.content_path,
        root_path=args.root_path,
        save_path=args.save_path,
        num_files=args.num_files,
        torrent_size=args.torrent_size,
        current_tracker=args.current_tracker,
        info_hash_v1=args.info_hash_v1,
        info_hash_v2=args.info_hash_v2,
        torrent_id=args.torrent_id,
    )

    # First, write to logfile.
    write_log(torrent_info)

    # Next, pause the torrent.
    if args.pause:
        pause_torrent(torrent_info.torrent_id)

    # Finally, tell the consumer where to pull this.
    if args.notify_url:
        notify_consumer(args.notify_url, torrent_info)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
