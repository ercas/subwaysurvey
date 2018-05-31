#!/usr/bin/env python3

import csv
import sys

from db import TStationDB

class CsvImporter(object):

    def __init__(self, *db_init_args, **db_init_kwargs):
        """ Initialize CsvImporter object

        All arguments will be passed to the db.TStationDB constructor
        """

        self.db = TStationDB(*db_init_args, **db_init_kwargs)
        self.column_label_map = []
        self.timestamp_column = "TIME"

    def map_column(self, data_column, label):
        """ Map a column in the CSV file to a sensor label in the database

        :param str data_column: The column in the CSV file containing data
        :param str label: The sensor label to be used for that data
        """

        self.column_label_map.append((data_column, label))

    def set_timestamp_column(self, timestamp_column):
        """ Change the name of the column to extract timestamps from (default:
        "TIME")

        :param str timestamp_column: The name of the column containing
            timestamps
        """

        self.timestamp_column = timestamp_column

    def import_csv(self, csv_path):
        """ Import a CSV file using the defined data column -> sensor label map

        :param str csv_path: The path to the CSV File
        """

        if (len(self.column_label_map) == 0):
            raise Exception("empty column label map")

        with open(csv_path, "r") as f:
            for row in csv.DictReader(f):
                timestamp = row[self.timestamp_column]
                try:
                    (location, position, status) = self.db.timestamp_to_location_status(timestamp)
                    for (data_column, label) in self.column_label_map:
                        self.db.record(label, row[data_column], location, position, status, timestamp)
                except TypeError:
                    print("no data exists for timestamp %s" % timestamp)
        self.db.commit()

class Dylos(CsvImporter):
    def __init__(self, *args, **kwargs):
        """ Initialize CsvImporter subclass that imports Dylos data """

        CsvImporter.__init__(self, *args, **kwargs)
        self.map_column("SMALLPARTICLES", "dylos smallparticles")
        self.map_column("LARGEPARTICLES", "dylos largeparticles")

class ADXL345(CsvImporter):
    def __init__(self, *args, **kwargs):
        """ Initialize CsvImporter subclass that imports ADXL345 data """

        CsvImporter.__init__(self, *args, **kwargs)
        self.map_column("X", "adxl345 x axis raw")
        self.map_column("Y", "adxl345 y axis raw")
        self.map_column("Z", "adxl345 z axis raw")

        self.normalize_data("x")

    def normalize_data(self, axis):
        self.db.cursor.execute(
            "SELECT * FROM observations WHERE source_id = %s" % (
                self.db.resolve_id("source_ids", "adxl345 %s axis raw" % axis)
            )
        )
        for row in self.db.cursor:
            value = row[5]
            row = list(row)
            print(value)
        print("ok")

if (__name__ == "__main__"):
    #Dylos().import_csv(sys.argv[1])
    ADXL345().import_csv(sys.argv[1])
