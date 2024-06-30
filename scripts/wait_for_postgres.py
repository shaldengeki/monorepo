#!/usr/bin/env python3

import os
import subprocess
import sys
import time

import pg8000.native


def wait_for_postgres() -> None:
    while True:
        try:
            pg8000.native.Connection(
                os.getenv("DB_USERNAME", "admin"),
                host=os.getenv("DB_HOST", "pg"),
                port=os.getenv("DB_PORT", 5432),
                database=os.getenv("DATABASE_NAME", "api_development"),
                password=os.getenv("DB_PASSWORD", "development"),
            )
        except pg8000.exceptions.InterfaceError:
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
