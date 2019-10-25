#!/usr/bin/env python
import csv
import datetime
import sys

from app import db
from models.transaction import Transaction

def read_file(filename):
    rows_written = 0
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            t = Transaction(
                datetime.datetime.strptime(row['Date'], '%m/%d/%Y'),
                row['Description'],
                row['Original Description'],
                round(float(row["Amount"]*100)),
                row["Transaction Type"],
                row["Category"],
                row["Account Name"],
                row["Labels"],
                row["Notes"]
            )
            db.session.add(t)
            rows_written += 1
    db.session.commit()
    print("Wrote {num} transactions to database".format(
        num=rows_written
    ))

if __name__ == '__main__':
    read_file(sys.argv[1])