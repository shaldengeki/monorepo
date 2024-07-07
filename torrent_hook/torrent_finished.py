#!/usr/bin/env python3

import argparse
import json
import qbittorrentapi

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--torrent-name")
    parser.add_argument("--category")
    parser.add_argument("--tags")
    parser.add_argument("--content-path")
    parser.add_argument("--root-path")
    parser.add_argument("--save-path")
    parser.add_argument("--num-files")
    parser.add_argument("--torrent-size")
    parser.add_argument("--current-tracker")
    parser.add_argument("--info-hash-v1")
    parser.add_argument("--info-hash-v2")
    parser.add_argument("--torrent-id")
    parser.add_argument("--output")
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
        "torrent_id": args.torrent_id
    }
    with open(args.output, 'a') as finished_log:
        finished_log.write(json.dumps(invocation) + "\n")

def main() -> int:
    args = parse_args()
    write_log(args)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())