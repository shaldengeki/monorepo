#!/usr/bin/env python3

import argparse
import json
# import requests
import qbittorrentapi

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
    parser.add_argument("--log-file")
    parser.add_argument("--notify-url")
    parser.add_argument("--pause", type=bool, default=False)
    return parser.parse_args()

def write_log(log_file: str, args: argparse.Namespace):
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
        "torrent_id": args.torrent_id
    }
    with open(log_file, 'a') as finished_log:
        finished_log.write(json.dumps(invocation) + "\n")

def notify_consumer(notify_url: str, args: argparse.Namespace) -> None:
    pass


def pause_torrent(torrent_id: str) -> None:
    with qbittorrentapi.Client(host="localhost", port=8080) as client:
        client.torrents_pause([torrent_id])

def main() -> int:
    args = parse_args()
    
    # First, write to logfile.
    if args.log_file:
        write_log(args.log_file, args)

    # Next, tell the consumer where to pull this.
    if args.notify_url:
        notify_consumer(args.notify_url, args)

    # Finally, pause the torrent.
    if args.pause:
        pause_torrent(args.torrent_id)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())