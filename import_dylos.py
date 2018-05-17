#!/usr/bin/env python3

import csv
import sys

from db import TStationDB

with TStationDB() as db:
    with open(sys.argv[1], "r") as f:
        for row in csv.DictReader(f):
            timestamp = row["TIME"]
            try:
                (location, position, status) = db.timestamp_to_location_status(timestamp)
                print(location, status)
                db.record("dylos smallparticles", row["SMALLPARTICLES"], location, position, status, timestamp)
                db.record("dylos largeparticles", row["LARGEPARTICLES"], location, position, status, timestamp)
            except TypeError:
                print("no data exists for timestamp %s" % timestamp)
