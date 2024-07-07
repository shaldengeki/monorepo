#!/usr/bin/env python3

import argparse
import json

# import requests
import logging

import qbittorrentapi

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--torrent-name", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--tags", required=True)
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
    parser.add_argument("--pause", type=bool, default=False)
    return parser.parse_args()


def write_log(args: argparse.Namespace):
    invocation = {
        "torrent_name": args.torrent_name,
        "category": args.category,
        "tags": args.tags,
        "content_path": args.content_path,
        "root_path": args.root_path,
        "save_path": args.save_path,
        "num_files": args.num_files,
        "torrent-size": args.torrent_size,
        "current_tracker": args.current_tracker,
        "info_hash_v1": args.info_hash_v1,
        "info_hash_v2": args.info_hash_v2,
        "torrent_id": args.torrent_id,
    }
    logger.info(f"Received completed torrent: {json.dumps(invocation)}")


def notify_consumer(notify_url: str, args: argparse.Namespace) -> None:
    logger.info(f"Notifying consumer for torrent {args.torrent_id}")


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

    # First, write to logfile.
    write_log(args)

    # Next, tell the consumer where to pull this.
    if args.notify_url:
        notify_consumer(args.notify_url, args)

    # Finally, pause the torrent.
    if args.pause:
        pause_torrent(args.torrent_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
