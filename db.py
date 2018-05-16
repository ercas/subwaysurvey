#!/usr/bin/env python3

import os
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
        :return: A boolean signifying if the database has been set up
        """

        self.db_path = path
        self.id_cache = {}
        self.auto_commit_interval = auto_commit_interval
        self.i = 0
        self.setup = False
        if (not os.path.isfile(self.db_path)):
            self.setup = True

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

        if (self.setup):
            self._setup()

    def _setup(self):
        print("intializing new database")
        for id_table in ["source_ids", "location_ids"]:
            self.cursor.execute("""
                CREATE TABLE %s(
                    id INTEGER PRIMARY KEY,
                    name VARCHAR UNIQUE
                )
            """ % id_table)
        self.cursor.execute("""
            CREATE TABLE observations(
                timestamp FLOAT,
                source_id INTEGER,
                location_id INTEGER,
                value FLOAT,
                notes VARCHAR,
                FOREIGN KEY(source_id) REFERENCES source_ids(id),
                FOREIGN KEY(location_id) REFERENCES location_ids(id)
            )
        """)
        self.connection.commit()

    def _check_auto_commit(self):
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

    def record(self, source_name, location_name, value, timestamp = None,
               notes = None):
        """ Record a timestamped observation to the database

        :param str source_name: The name of the source
        :param str location_name: The name of the location
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
                    INSERT INTO observations(timestamp, source_id, location_id, value, notes)
                    VALUES (?, ?, ?, ?, ?)
                """,
                (
                    timestamp, self.resolve_id("source_ids", source_name),
                    self.resolve_id("location_ids", location_name),
                    value, notes
                )
            )
            self._check_auto_commit()
        except sqlite3.OperationalError:
            print("database busy, trying again...")
            self.record(source_name, location_name, value, timestamp, notes)

    def commit(self):
        """ Wrapper for SQLite3 connection commit that resets the
        _check_auto_commit counter """

        self.i = 0
        self.connection.commit()

    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.connection.commit()

class TStationDB(DB):

    def __init__(self, *args, **kwargs):
        """ Initialize database that extends the DB class with functionality
        for recording MBTA stations """

        DB.__init__(self, *args, **kwargs)

        if (self.setup):
            print("initializing location history tables")
            self.cursor.execute("""
                CREATE TABLE status_ids(
                    id INTEGER PRIMARY KEY,
                    name VARCHAR UNIQUE
                )
            """)
            self.cursor.execute("""
                CREATE TABLE location_history(
                    timestamp FLOAT,
                    location_id INTEGER,
                    status_id INTEGER,
                    FOREIGN KEY(location_id) REFERENCES location_ids(id),
                    FOREIGN KEY(status_id) REFERENCES status_ids(id)
                )
            """)

            # modify the observations table so that it has an additional
            # status_id column
            self.cursor.execute("DROP TABLE observatoins")
            self.cursor.execute("""
                CREATE TABLE observations(
                    timestamp FLOAT,
                    source_id INTEGER,
                    location_id INTEGER,
                    status_id INTEGER,
                    value FLOAT,
                    notes VARCHAR,
                    FOREIGN KEY(source_id) REFERENCES source_ids(id),
                    FOREIGN KEY(location_id) REFERENCES location_ids(id)
                    FOREIGN KEY(status_id) REFERENCES status_ids(id)
                )
            """)
            self.connection.commit()


    def record_location(self, location_name, status_name, timestamp = None):
        """ Record a timestamped observation to the database

        :param str location_name: The name of the location
        :param str status_name: The status of the location (entering,
            leaving, stopped, etc)
        :param float timestamp: The time that the observation was taken; defaults
            to the current system time
        """

        if (timestamp is None):
            timestamp = time.time()

        try:
            self.cursor.execute(
                """
                    INSERT INTO location_history(timestamp, location_id, status_id)
                    VALUES (?, ?, ?)
                """,
                (
                    timestamp, self.resolve_id("location_ids", location_name),
                    self.resolve_id("status_ids", status_name)
                )
            )
            self._check_auto_commit()
        except sqlite3.OperationalError:
            print("database busy, trying again...")
            self.record(source_name, location_name, value, timestamp, notes)

if (__name__ == "__main__"):
    db = TStationDB()
