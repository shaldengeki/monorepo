#!/usr/bin/env python
# Imports Mint transactions.
# Expects a Mint-exported CSV as the first argument.
# To invoke, do something like:
# docker run -it shaldengeki/home-api:edge /usr/bin/env python -m api.scripts.import_data /path/to/transactions.csv

import csv
import datetime
import sys

from home_api.api.models.transaction import Transaction
from home_api.config import db


def read_file(filename):
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
    read_file(sys.argv[1])
