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
        """

        self.db_path = path
        self.id_cache = {}
        self.auto_commit_interval = auto_commit_interval
        self.i = 0

        setup = False
        if (not os.path.isfile(self.db_path)):
            setup = True

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

        if (setup):
            print("intiializing new database")
            for id_table in ["sources", "locations"]:
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS %s(
                        id INTEGER PRIMARY KEY,
                        name VARCHAR UNIQUE
                    )
                """ % id_table)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS observations(
                    timestamp FLOAT,
                    source_id INTEGER,
                    location_id INTEGER,
                    value FLOAT,
                    notes VARCHAR,
                    FOREIGN KEY(source_id) REFERENCES sources(id),
                    FOREIGN KEY(location_id) REFERENCES locations(id)
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
                    timestamp, self.resolve_id("sources", source_name),
                    self.resolve_id("locations", location_name),
                    value, notes)
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
