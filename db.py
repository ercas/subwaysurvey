#!/usr/bin/env python3
# facilities for storing data

import csv
import os
import sqlite3
import time

MAX_EXEC_RETRIES = 10
FAILED_EXEC_LOG = "failed_exec.txt"
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
        self.setup = False
        if (not os.path.isfile(self.db_path)):
            self.setup = True

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

        if (self.setup):
            self._setup()

    def _setup(self):
        """ Initialize new database, assuming it doesn't exist yet """

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

    def record(self, source_name, value, location_name = None,
               timestamp = None, notes = None):
        """ Record a timestamped observation to the database

        :param str source_name: The name of the source
        :param float value: The value of the observation
        :param str location_name: The name of the location
        :param float timestamp: The time that the observation was taken; defaults
            to the current system time
        :param str notes: Additional notes to accompany the observation, if any
        """

        if (timestamp is None):
            timestamp = time.time()

        self._exec(
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
            for id_table in ["position_ids", "status_ids"]:
                self.cursor.execute("""
                    CREATE TABLE %s(
                        id INTEGER PRIMARY KEY,
                        name VARCHAR UNIQUE
                    )
                """ % id_table)
            self.cursor.execute("""
                CREATE TABLE location_history(
                    timestamp FLOAT NOT NULL,
                    location_id INTEGER NOT NULL,
                    position_id INTEGER NOT NULL,
                    status_id INTEGER NOT NULL,
                    FOREIGN KEY(location_id) REFERENCES location_ids(id),
                    FOREIGN KEY(position_id) REFERENCES position_ids(id),
                    FOREIGN KEY(status_id) REFERENCES status_ids(id)
                )
            """)

            # modify the observations table so that it has an additional
            # status_id column
            self.cursor.execute("DROP TABLE observations")
            self.cursor.execute("""
                CREATE TABLE observations(
                    timestamp FLOAT,
                    source_id INTEGER NOT NULL,
                    location_id INTEGER,
                    position_id INTEGER,
                    status_id INTEGER,
                    value FLOAT NOT NULL,
                    notes VARCHAR,
                    FOREIGN KEY(source_id) REFERENCES source_ids(id),
                    FOREIGN KEY(location_id) REFERENCES location_ids(id),
                    FOREIGN KEY(position_id) REFERENCES position_ids(id),
                    FOREIGN KEY(status_id) REFERENCES status_ids(id)
                )
            """)
            self.connection.commit()

    # overwrite the record function with additional location_status arg
    def record(self, source_name, value, location_name = None,
               position_name = None, status_name = None, timestamp = None,
               notes = None):
        """ Record a timestamped observation to the database

        :param str source_name: The name of the source
        :param float value: The value of the observation
        :param str location_name: The name of the location
        :param str position_name: The name of the position
        :param str status_name: The status of the location (entering,
            leaving, stopped, etc)
        :param float timestamp: The time that the observation was taken; defaults
            to the current system time
        :param str notes: Additional notes to accompany the observation, if any
        """

        if (timestamp is None):
            timestamp = time.time()

        self._exec(
            """
                INSERT INTO observations(timestamp, source_id, location_id, position_id, status_id, value, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp, self.resolve_id("source_ids", source_name),
                self.resolve_id("location_ids", location_name),
                self.resolve_id("position_ids", location_name),
                self.resolve_id("status_ids", status_name),
                value, notes
            )
        )


    def record_location(self, location_name, position_name, status_name, timestamp = None):
        """ Record a timestamped observation to the database

        :param str location_name: The name of the location
        :param str status_name: The status of the location (entering,
            leaving, stopped, etc)
        :param str position_name: The position at the location (subway car,
            platform center, etc)
        :param float timestamp: The time that the observation was taken; defaults
            to the current system time
        """

        if (timestamp is None):
            timestamp = time.time()

        self._exec(
            """
                INSERT INTO location_history(timestamp, location_id, position_id, status_id)
                VALUES (?, ?, ?, ?)
            """,
            (
                timestamp,
                self.resolve_id("location_ids", location_name),
                self.resolve_id("position_ids", position_name),
                self.resolve_id("status_ids", status_name)
            )
        )

    def timestamp_to_location_status(self, timestamp):
        """ Get the location and status that was occurring at a particular time

        :param float timestamp: The timestamp to query
        :return: A tuple of the location id and status id, or None if there is
            no prior location history
        :rtype: tuple or None
        """

        self.cursor.execute(
            """
                SELECT location_ids.name, position_ids.name, status_ids.name
                FROM location_history
                INNER JOIN location_ids
                    ON location_ids.id = location_history.location_id
                INNER JOIN position_ids
                    ON position_ids.id = location_history.position_id
                INNER JOIN status_ids
                    ON status_ids.id = location_history.status_id
                WHERE location_history.timestamp < ?
                ORDER BY location_history.rowid DESC
                LIMIT 1
            """,
            (timestamp,)
        )
        try:
            return self.cursor.fetchone()
        except TypeError:
            return None

    def observations_to_csv(self, output_file):
        """ Join tables and write observations to csv files

        :param str output_file: The file to write data to
        """
        with open(output_file, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "source", "location", "position", "status", "value", "notes"])
            self.cursor.execute(
                """
                    SELECT observations.timestamp, source_ids.name, location_ids.name, position_ids.name, status_ids.name, observations.value, observations.notes
                    FROM observations
                    INNER JOIN source_ids
                        ON source_ids.id = observations.source_id
                    INNER JOIN location_ids
                        ON location_ids.id = observations.location_id
                    INNER JOIN position_ids
                        ON position_ids.id = location_history.position_id
                    INNER JOIN status_ids
                        ON status_ids.id = observations.status_id
                """
            )
            for row in self.cursor:
                writer.writerow(row)
        print("wrote to %s" % output_file)

if (__name__ == "__main__"):
    with TStationDB() as db:
        db.record("dylos", 1)
        db.record("dylos", 2)
        db.record("dylos", 3)
        db.record("dylos", 4)
