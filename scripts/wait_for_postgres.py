#!/usr/bin/env python3

import os
import subprocess
import sys
import time
from urllib.parse import urlparse

import pg8000.native  # type: ignore

from base.flask_app import database_uri


def wait_for_postgres() -> None:
    uri = database_uri()
    parsed_uri = urlparse(uri)
    username = "admin"
    password = "development"
    host = "localhost"
    port = "5432"
    database = "postgres"
    if "@" not in parsed_uri.netloc:
        # no user/password.
        host_parts = parsed_uri.netloc
    else:
        auth_parts, host_parts = parsed_uri.netloc.split("@")
        if ":" not in auth_parts:
            username = auth_parts
        else:
            username, password = auth_parts.split(":")

    if ":" not in host_parts:
        host = host_parts
    else:
        host, port = host_parts.split(":")

    if parsed_uri.path and parsed_uri.path != "/":
        database = parsed_uri.path[1:]

    while True:
        print(f"Attempting connection to host {host} and port {port}...")
        try:
            pg8000.native.Connection(
                username,
                host=host,
                port=int(port),
                database=database,
                password=password,
                ssl_context=False,
            )
        except pg8000.exceptions.InterfaceError:  # type: ignore
            print("Postgres is unavailable - sleeping")
            time.sleep(1)
            continue
        else:
            break

    print("Postgres is up - executing command")


if __name__ == "__main__":
    wait_for_postgres()
    if sys.argv[1:]:
        subprocess.run(sys.argv[1:])
