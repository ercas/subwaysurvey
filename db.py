#!/usr/bin/env python3
# facilities for storing data

import csv
import os
import sqlite3
import time

MAX_EXEC_RETRIES = 10
FAILED_EXEC_LOG = "failed_exec.txt"
DEFAULT_DB_PATH = "data.db"
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
        self.setup = False
        if (not os.path.isfile(self.db_path)):
            self.setup = True

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

        if (self.setup):
            self._setup()

    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.connection.commit()

    def _setup(self):
        """ Initialize new database, assuming it doesn't exist yet """

        print("intializing new database")

        for id_table in ["id_sensor", "id_location", "id_position", "id_status"]:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS %s(
                    id INTEGER PRIMARY KEY,
                    name VARCHAR UNIQUE
                )
            """ % id_table)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS location_history(
                timestamp FLOAT NOT NULL,
                location_id INTEGER NOT NULL,
                position_id INTEGER NOT NULL,
                status_id INTEGER NOT NULL,
                FOREIGN KEY(location_id) REFERENCES id_location(id),
                FOREIGN KEY(position_id) REFERENCES id_position(id),
                FOREIGN KEY(status_id) REFERENCES id_status(id)
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

    def _exec(self, sql_str, sql_args, attempt = 1):
        """ Wrapper around sqlite3.Cursor.execute that automatically retries
        and dumps to a file if the max number of retries have been made

        :param str sql_str: The string to be executed
        :param tuple sql_args: The arguments to use in the string
        :param int attempt: **DO NOT USE**: information about how many tries
            have been attempted
        """
        try:
            self.cursor.execute(sql_str, sql_args)
            self._check_auto_commit()
        except sqlite3.OperationalError as err:
            print("ERROR: %s" % err)
            if (attempt < MAX_EXEC_RETRIES):
                print("trying again...")
                time.sleep(0.001)
                self._exec(sql_str, sql_args)
            else:
                print("max attempts tried; dumping to %s instead" % FAILED_EXEC_LOG)
                with open(FAILED_EXEC_LOG, "r") as f:
                    f.write("%s\t%s\n" % (sql_str, list(sql_args)))

    def resolve_id(self, table, name):
        """ Resolve a name to an id

        :param str name: The name of the item
        :return: An integer corresponding to the item's id in the table, or
            None if the name is none
        :rtype: int or None
        """

        if (name is None):
            return None
        else:
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

    def commit(self):
        """ Wrapper for SQLite3 connection commit that resets the
        _check_auto_commit counter """

        self.i = 0
        self.connection.commit()

    def import_timestamps(self, timestamp_file):
        with open(timestamp_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.cursor.execute(
                    """
                        INSERT INTO location_history(
                            timestamp, location_id, position_id, status_id
                        )
                        VALUES (?, ?, ?, ?)
                    """,
                    (
                        row["TIMESTAMP"],
                        self.resolve_id("id_location", row["LOCATION"]),
                        self.resolve_id("id_position", row["POSITION"]),
                        self.resolve_id("id_status", row["STATUS"])
                    )
                )
            self.connection.commit()

    def Sensor(self, sensor_name):
        return Sensor(self, sensor_name)

class Sensor(object):

    def __init__(self, db, sensor_name):
        self.db = db
        self.sensor_name = sensor_name

        self.db.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_%s(
                timestamp FLOAT NOT NULL,
                value FLOAT NOT NULL,
                notes VARCHAR
            )
        """ % self.sensor_name)
        self.db.connection.commit()

    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.db.connection.commit()

    def record(self, value, notes = None, timestamp = None):
        if (timestamp is None):
            timestamp = time.time()

        self.db.cursor.execute(
            """
                INSERT INTO sensor_%s(timestamp, value, notes)
                VALUES (?, ?, ?)
            """ % self.sensor_name,
            (timestamp, value, notes)
        )
        self.db._check_auto_commit()

if (__name__ == "__main__"):
    with DB() as db:
        with db.Sensor("dylos") as dylos:
            dlos.record(1)
