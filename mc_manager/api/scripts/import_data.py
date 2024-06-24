#!/usr/bin/env python
# Imports currently-running servers.
# To invoke, do something like:
# docker run -it shaldengeki/mc-manager-api:edge /usr/bin/env python -m api.scripts.import_data

import csv
import datetime
import subprocess
import sys

from ..app import db
from ..models.server import Server


def read_servers():
    rows_written = 0
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            t = Transaction(
                date=datetime.datetime.strptime(row["Date"], "%m/%d/%Y"),
                description=row["Description"],
                original_description=row["Original Description"],
                amount=round(float(row["Amount"]) * 100),
                type=row["Transaction Type"],
                category=row["Category"],
                account=row["Account Name"],
                labels=row["Labels"],
                notes=row["Notes"],
            )
            db.session.add(t)
            rows_written += 1
    db.session.commit()
    print("Wrote {num} transactions to database".format(num=rows_written))


if __name__ == "__main__":
    read_servers()
