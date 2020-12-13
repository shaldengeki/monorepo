#!/usr/bin/env python3

import argparse
import docker
import logging
import os
import requests


def parse_args():
    parser = argparse.ArgumentParser(description="Update minecraft server status.")
    parser.add_argument(
        "--api-host",
        default=os.environ.get("API_HOST", "api"),
        help="API hostname that can be queried to fetch minecraft server listing.",
    )
    parser.add_argument(
        "--api-port",
        default=os.environ.get("API_PORT", "5000"),
        help="API port that can be queried to fetch minecraft server listing.",
    )
    return parser.parse_args()


def run(host, port):
    # First, get the list of minecraft servers we should poll status for.
    servers = fetch_expected_servers(host, port)

    # Next, get a list of actively-running servers.
    client = docker.from_env()
    print(client.containers.list())

    # For each server we expect to poll,
    # update the status accordingly.
    for server in servers:
        pass


def fetch_expected_servers(host, port):
    url = f"http://{host}:{port}/graphql"
    logging.info(f"Fetching server list from {url}")
    response = requests.post(
        url,
        data={
            "query": "query {\n  servers {\n    id,\n    name,\n    latestLog {\n      id\n      created\n      state\n      error\n    }\n  }\n}",
            "variables": None,
        },
    )
    return response.get("data", {}).get("servers", [])


if __name__ == "__main__":
    args = parse_args()
    run(args.api_host, args.api_port)
