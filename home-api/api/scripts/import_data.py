#!/usr/bin/env python
import csv
import datetime
import sys

from app.app import db
from app.models.transaction import Transaction

def read_file(filename):
    rows_written = 0
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            t = Transaction(
                date=datetime.datetime.strptime(row['Date'], '%m/%d/%Y'),
                description=row['Description'],
                original_description=row['Original Description'],
                amount=round(float(row["Amount"])*100),
                type=row["Transaction Type"],
                category=row["Category"],
                account=row["Account Name"],
                labels=row["Labels"],
                notes=row["Notes"]
            )
            db.session.add(t)
            rows_written += 1
    db.session.commit()
    print("Wrote {num} transactions to database".format(
        num=rows_written
    ))


if __name__ == '__main__':
    read_file(sys.argv[1])
