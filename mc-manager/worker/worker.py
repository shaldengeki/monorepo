#!/usr/bin/env python3

import argparse
import boto3
from boto3.exceptions import S3UploadFailedError
import datetime
import docker
import json
import logging
import os
import requests
import tarfile
import time


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
        type=int,
        help="API port that can be queried to fetch minecraft server listing.",
    )
    parser.add_argument(
        "--host-path",
        default=os.environ.get("HOST_PATH", "/var/minecraft"),
        help="Absolute path to where minecraft server data is stored. Servers should be stored underneath this path.",
    )
    parser.add_argument(
        "--backup-interval",
        default=os.environ.get("BACKUP_INTERVAL", (60 * 60 * 24)),
        type=int,
        help="Interval between server backups, in seconds.",
    )
    parser.add_argument(
        "--s3-bucket",
        default=os.environ.get("S3_BUCKET"),
        help="Name of the S3 bucket that backups should be uploaded to.",
    )
    parser.add_argument(
        "--update-interval",
        default=300.0,
        type=float,
        help="Interval between server polling updates, in seconds.",
    )
    return parser.parse_args()


def run(args):
    host, port = args.api_host, args.api_port
    update_interval = args.update_interval

    host_path = args.host_path
    backup_interval = args.backup_interval
    s3 = boto3.resource("s3")
    s3_bucket = args.s3_bucket

    while True:
        # First, get the list of minecraft servers we should poll status for.
        servers = fetch_expected_servers(host, port) or []

        # Next, get a list of actively-running servers.
        client = docker.from_env()
        containers = client.containers.list()

        # For each server we expect to poll,
        # update the status accordingly.
        for server in servers:
            update_server_status(host, port, server, containers)
            back_up_server(
                host, port, server, host_path, backup_interval, s3, s3_bucket
            )
            clean_up_backups(host, port, server, s3)

        time.sleep(update_interval)


def query_graphql(host: str, port: int, data: dict) -> dict:
    url = f"http://{host}:{port}/graphql"
    logging.error(f"Querying GraphQL API at {url} with data {data}")
    response = requests.post(
        url,
        data=data,
    ).json()
    logging.error(f"Response: {response}")
    return response


def fetch_expected_servers(host: str, port: int) -> list:
    # TODO: only select servers for which the latest log is active
    logging.error(f"Fetching server list")
    response = query_graphql(
        host,
        port,
        {
            "query": """
                query {
                    servers {
                        id,
                        name,
                        latestBackup {
                            created
                        }
                    }
                }""",
            "variables": None,
        },
    )
    return response.get("data", {}).get("servers", [])


def update_server_status(host: str, port: int, server: dict, containers: list) -> dict:
    logging.error(f"Updating status for server {server['name']}")
    container = [c for c in containers if c.name == server["name"]]
    if not container:
        logging.error(f"Server {server['name']} is no longer running")
        # Record that this server is no longer running.
        return record_server_status(host, port, int(server["id"]), "stopped")
    else:
        logging.error(f"Server {server['name']} is running")
        # Record that this server is running.
        return record_server_status(host, port, int(server["id"]), "started")


def record_server_status(host: str, port: int, server_id: int, status: str) -> dict:
    logging.error(f"Recording server status")
    response = query_graphql(
        host,
        port,
        {
            "query": """
                mutation createLog($id:Int!, $state:ServerLogState!) {
                    createServerLog(serverId: $id, state: $state) {
                        id
                        created
                        state
                        error
                    }
                }""",
            "variables": json.dumps({"id": server_id, "state": status}),
            "operationName": "createLog",
        },
    )
    return response.get("data", {}).get("createServerLog")


def back_up_server(
    host: str,
    port: int,
    server: dict,
    host_path: str,
    backup_interval: int,
    s3,
    s3_bucket: str,
) -> None:
    # Halt early if the server shouldn't be backed up.
    latest_backup = server["latestBackup"]
    if latest_backup is not None:
        latest_backup_time = latest_backup["created"]
        seconds_since_backup = (
            datetime.datetime.utcnow().timestamp() - latest_backup_time
        )
        if seconds_since_backup < backup_interval:
            logging.error(
                f"Last backup for server {server['name']} was performed {seconds_since_backup}s ago, skipping this round"
            )
            return

    # Create a new server backup entry.
    logging.error(f"Recording server backup entry")
    response = query_graphql(
        host,
        port,
        {
            "query": """
                mutation createServerBackup($serverId:Int!, $state:ServerBackupState!) {
                    createServerBackup(serverId:$serverId, state:$state) {
                        id
                    }
                }""",
            "variables": json.dumps({"serverId": server["id"], "state": "started"}),
            "operationName": "createServerBackup",
        },
    )
    backup_entry = response.get("data", {}).get("createServerBackup")

    # Start backing the server up.
    # First, zip up the state of the server.
    logging.error(f"Zipping up server for backup")
    file_name = f"{server['name']}-{datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')}.tar.gz"
    file_path = os.path.join("/tmp", file_name)
    os.chdir(host_path)
    with tarfile.open(file_path, "w:gz") as tar:
        tar.add(server["name"])

    remote_path = f"s3://{s3_bucket}/{server['name']}/{file_name}"

    # Next, upload the zipfile to S3.
    logging.error(f"Uploading zipped backup at {file_path} to s3 at {remote_path}")
    error = None
    try:
        s3.meta.client.upload_file(
            file_path, s3_bucket, f"{server['name']}/{file_name}"
        )
    except S3UploadFailedError as e:
        logging.error(f"Uploading backup to S3 failed with error {e}")
        error = e.message

    # Either way, delete the temporary backup.
    logging.error(f"Deleting temporary backup at {file_path}")
    os.remove(file_path)

    if error is None:
        # If successful, record that the backup is complete.
        logging.error(f"Recording server backup completed")
        state = "completed"
    else:
        logging.error(f"Recording server backup failed")
        state = "failed"
        remote_path = None

    query_graphql(
        host,
        port,
        {
            "query": """
                mutation updateServerBackup($id:Int!, $state:ServerBackupState!, $error:String, $remotePath:String) {
                    updateServerBackup(id:$id, state:$state, error:$error, remotePath:$remotePath) {
                        id
                        state
                        error
                        remotePath
                    }
                }""",
            "variables": json.dumps(
                {
                    "id": int(backup_entry["id"]),
                    "state": state,
                    "error": error,
                    "remotePath": remote_path,
                }
            ),
            "operationName": "updateServerBackup",
        },
    )


def clean_up_backups(host: str, port: int, server: dict, s3) -> list:
    # Get this server and the list of backups that exist.
    logging.error(f"Fetching backups for server {server['name']}")
    response = query_graphql(
        host,
        port,
        {
            "query": """
                query serverBackups($serverId:Int!) {
                    serverBackups(serverId: $serverId, state:completed) {
                        id
                        created
                        remotePath
                    }
                }""",
            "variables": json.dumps({"serverId": server["id"]}),
            "operationName": "serverBackups",
        },
    )
    if "errors" in response:
        logging.error(
            f"Error encountered while cleaning up backups: {response['errors']}"
        )
        return

    # Select just the N oldest backups for this server.
    backups = response.get("data", {}).get("serverBackups", [])
    logging.error(f"{len(backups)} backups found")
    backups = sorted(backups, key=lambda b: b["created"], reverse=True)
    to_delete = backups[7:]

    # Delete those backups.
    for backup in to_delete:
        logging.error(f"Deleting backup at {backup['remotePath']}")
        remote_path = backup["remotePath"]
        if remote_path.startswith("s3://"):
            remote_path = remote_path[6:]
        path_parts = remote_path.split("/")
        bucket = path_parts[0]
        key = "/".join(path_parts[1:])
        s3.meta.client.delete_object(Bucket=bucket, Key=key)
    return to_delete


if __name__ == "__main__":
    args = parse_args()
    run(args)
