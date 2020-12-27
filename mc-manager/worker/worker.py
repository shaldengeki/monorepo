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
import shutil
import tarfile
import time
from typing import Optional


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

        running_servers = [
            server
            for server in servers
            if server.get("latestLog", {}).get("state") == "started"
        ]

        # Next, get a list of actively-running servers.
        client = docker.from_env()
        containers = client.containers.list()
        container_names = set(c.name for c in containers)

        # For each server we expect to poll,
        # update the status accordingly.
        for server in running_servers:
            update_server_status(host, port, server, container_names)
            back_up_server(
                host, port, server, host_path, backup_interval, s3, s3_bucket
            )
            clean_up_backups(host, port, server, s3)

        # Next, get the list of minecraft servers that we should restore from backup.
        server_restorations = [
            server
            for server in servers
            if server.get("latestLog", {}).get("state") == "restore_queued"
        ]
        for server in server_restorations:
            process_server_restoration(
                client, containers, server, host, port, host_path, s3
            )

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


def split_s3_path(path: str) -> tuple:
    if path.startswith("s3://"):
        path = path[5:]
    path_parts = path.split("/")
    bucket = path_parts[0]
    key = "/".join(path_parts[1:])
    return (bucket, key)


def fetch_expected_servers(host: str, port: int) -> list:
    logging.error(f"Fetching server list")
    response = query_graphql(
        host,
        port,
        {
            "query": """
                query FetchServers {
                    servers {
                        id,
                        name,
                        createdBy
                        port
                        timezone
                        zipfile
                        motd
                        memory
                        latestBackup {
                            created
                        }
                        latestLog {
                            state
                            backup {
                                id
                                remotePath
                            }
                        }
                    }
                }""",
            "variables": None,
            "operationName": "FetchServers",
        },
    )
    return response.get("data", {}).get("servers", [])


def update_server_status(
    host: str, port: int, server: dict, container_names: list
) -> dict:
    logging.error(f"Updating status for server {server['name']}")
    if server["name"] in container_names:
        logging.error(f"Server {server['name']} is no longer running")
        # Record that this server is no longer running.
        return record_server_status(host, port, int(server["id"]), "stopped")
    else:
        logging.error(f"Server {server['name']} is running")
        # Record that this server is running.
        return record_server_status(host, port, int(server["id"]), "started")


def record_server_status(
    host: str, port: int, server_id: int, status: str, backup_id: str = None
) -> dict:
    logging.error(f"Recording server status")
    response = query_graphql(
        host,
        port,
        {
            "query": """
                mutation createLog($id:Int!, $state:ServerLogState!, $backupId:Int) {
                    createServerLog(serverId: $id, state: $state, backupId:$backupId) {
                        id
                        created
                        state
                        error
                    }
                }""",
            "variables": json.dumps(
                {"id": server_id, "state": status, "backupId": backup_id}
            ),
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
        bucket, key = split_s3_path(remote_path)
        s3.meta.client.delete_object(Bucket=bucket, Key=key)
    return to_delete


def process_server_restoration(
    client: docker.DockerClient,
    containers: list,
    server: dict,
    host: str,
    port: int,
    host_path: str,
    s3,
) -> None:
    logging.error(f"Processing server restoration for {server['name']}")
    backup_id = server.get("latestLog", {}).get("backup", {}).get("id")
    if backup_id is None:
        logging.error(
            f"Server {server['name']}'s active backup has no remote URL; aborting."
        )

        # Mark this server as failed.
        record_server_status(host, port, server["id"], "stopped")
        return

    # Set the state of this server, so nobody else picks it up.
    record_server_status(host, port, server["id"], "restore_started", backup_id)

    # Download the backup.
    backup_location = download_backup(s3, server)

    # Stop the current server if it exists.
    matching_container = next(
        (container for container in containers if container.name == server["name"]),
        None,
    )
    if matching_container is not None:
        logging.error(f"Stopping existing container with name {server['name']}")
        matching_container.stop()
        matching_container.remove()

    # Restore the server.
    restore_server(client, backup_location, server, host_path)

    # Mark this server as started.
    record_server_status(host, port, server["id"], "started")


def restore_server(
    docker_client: docker.DockerClient,
    backup_location: str,
    server: dict,
    host_path: str,
) -> None:
    # Delete any currently-existing files.
    server_path = f"{host_path}/{server['name']}"
    logging.error(f"Deleting existing files at {server_path}")
    shutil.rmtree(server_path)

    # Extract the backup to the canonical location.
    logging.error(f"Extracting backup to canonical location at {host_path}")
    os.chdir(host_path)
    with tarfile.open(backup_location, "r:gz") as tar:
        tar.extractall()

    # Start the server.
    start_container(docker_client, server, host_path)
    return


def download_backup(s3_client, server: dict) -> str:
    backup_path = server.get("latestLog", {}).get("backup", {}).get("remotePath")
    bucket, key = split_s3_path(backup_path)
    logging.error(f"Downloading backup from s3://{bucket}/{key} to /tmp")

    filename = os.path.basename(key)
    destination = f"/tmp/{filename}"
    s3_client.meta.client.download_file(bucket, key, destination)
    return destination


def start_container(
    docker_client: docker.DockerClient, server: dict, host_path: str
) -> None:
    logging.error(
        f"Starting container for server {server['name']} on port {server['port']}: {server}"
    )
    docker_client.containers.run(
        "itzg/minecraft-server",
        detach=True,
        ports={int(server["port"]): 25565},
        name=server["name"],
        volumes={f"{host_path}/{server['name']}": {"bind": "/data", "mode": "rw"}},
        environment={
            "EULA": "TRUE",
            "TZ": server.get("timezone", "America/Los Angeles"),
            "TYPE": "CURSEFORGE",
            "CF_SERVER_MOD": server["zipfile"],
            "OVERRIDE_SERVER_PROPERTIES": "true",
            "SERVER_NAME": server["name"],
            "DIFFICULTY": "normal",
            "OPS": server["createdBy"],
            "ENABLE_COMMAND_BLOCK": "false",
            "SPAWN_PROTECTION": "0",
            "MOTD": server["motd"],
            "MEMORY": server["memory"],
        },
    )


if __name__ == "__main__":
    args = parse_args()
    run(args)
