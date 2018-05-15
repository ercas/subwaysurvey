#!/usr/bin/env python3

import sqlite3
import time

DEFAULT_DB_PATH = "observations.db"
AUTO_COMMIT_INTERVAL = 1000
LOCATION_SOURCE_ID = "location"

class DB(object):

    def __init__(self, path = DEFAULT_DB_PATH,
                 auto_commit_interval = AUTO_COMMIT_INTERVAL):
        """ Initialize generic sensor data recording database

        :param str path: The path that the database will be stored at
        :param int auto_commit_interval: The number of inserts after which a
            database commit will be forced
        """

        self.auto_commit_interval = auto_commit_interval
        self.i = 0

        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_ids(
                id INTEGER PRIMARY KEY,
                name VARCHAR UNIQUE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS observations(
                timestamp FLOAT,
                source_id INTEGER,
                value FLOAT,
                notes VARCHAR,
                FOREIGN KEY(source_id) REFERENCES source_ids(id)
            )
        """)
        self.connection.commit()
        self.id_cache = {}

    def check_auto_commit(self):
        """ Automatically commit data to the database if the number of observations
        since the last commit has passed the threshold """

        self.i += 1
        if (self.i % self.auto_commit_interval == 0):
            print("forcing commit - %d inserts" % (self.i))
            self.connection.commit()

    def resolve_id(self, table, name):
        """ Resolve a name to an id

        :param str name: The name of the item
        :return: An integer corresponding to the item's id in the table
        :rtype: int
        """

        if (table in self.id_cache):
            id_dict = self.id_cache[table]
        else:
            self.cursor.execute("SELECT * FROM %s" % table)
            id_dict = {
                row[1]: row[0]
                for row in self.cursor
            }
            self.id_cache[table] = id_dict

        if (name in id_dict):
            return id_dict[name]
        else:
            self.cursor.execute(
                """
                    INSERT OR IGNORE INTO %s(name)
                    VALUES (?)
                """ % table,
                (name,)
            )
            self.commit()
            self.cursor.execute(
                "SELECT * FROM %s WHERE name = ?" % table,
                (name,)
            )
            id_ = self.cursor.fetchone()[0]
            self.id_cache[table][name] = id_
            return id_

    def record(self, source_name, value, timestamp = None, notes = None):
        """ Record a timestamped observation to the database

        :param str source_name: The name of the source
        :param float value: The value of the observation
        :param float timestamp: The time that the observation was taken; defaults
            to the current system time
        :param str notes: Additional notes to accompany the observation, if any
        """

        if (timestamp is None):
            timestamp = time.time()

        try:
            self.cursor.execute(
                """
                    INSERT INTO observations(timestamp, source_id, value)
                    VALUES (?, ?, ?)
                """,
                (timestamp, self.resolve_id("source_ids", source_name), value)
            )
            self.check_auto_commit()
        except sqlite3.OperationalError:
            print("database busy, trying again...")
            self.record(value)

    def commit(self):
        """ Wrapper for SQLite3 connection commit that resets the
        check_auto_commit counter """

        self.i = 0
        self.connection.commit()

    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.connection.commit()

class TStopDB(DB):

    def __init__(self, *args, **kwargs):
        """ Initialize TStopDB - extends DB with facilities for recording T
        stop enter/leave times """

        DB.__init__(self, *args, **kwargs)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS station_ids(
                id INTEGER PRIMARY KEY,
                name VARCHAR
            )
        """)
        self.connection.commit()

    def update_location(self, station, status):
        try:
            self.record(
                LOCATION_SOURCE_ID, self.resolve_id("station_ids", station),
                notes = status
            )
            self.check_auto_commit()
        except sqlite3.OperationalError:
            print("database busy, trying again...")
            self.record(station, status)

with TStopDB() as db:
    while True:
        db.record("dylos", 1)
        db.record("dylos2", 1)
        db.record("dylos3", 1)
        db.update_location("copley", "entering")
        db.update_location("copley", "stopped")
        db.update_location("copley", "leaving")
