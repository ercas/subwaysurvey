#!/usr/bin/env python3

import dateutil.parser
import csv
import os
import sys

from db import DB

DATA_DIR = "./data/"
if (not os.path.isdir(DATA_DIR)):
    os.makedirs(DATA_DIR)

class CsvImporter(object):

    def __init__(self, *db_init_args, **db_init_kwargs):
        """ Initialize CsvImporter object

        All arguments will be passed to the db.TStationDB constructor
        """

        self.db = DB(*db_init_args, **db_init_kwargs)
        self.column_table_map = []
        self.timestamp_column = "TIME"

    def set_data_column(self, data_column, table_name):
        """ Map a column in the CSV file to a sensor label in the database

        :param str data_column: The column in the CSV file containing data
        :param str table_name: The table to be used for that data
        """

        self.column_table_map.append((data_column, self.db.Sensor(table_name.replace(" ", "_"))))

    def set_timestamp_column(self, timestamp_column):
        """ Change the name of the column to extract timestamps from (default:
        "TIME")

        :param str timestamp_column: The name of the column containing
            timestamps
        """

        self.timestamp_column = timestamp_column

    def import_csv(self, csv_path, append_location_data = False):
        """ Import a CSV file using the defined data column -> sensor label map

        :param str csv_path: The path to the CSV File
        """

        if (len(self.column_table_map) == 0):
            raise Exception("empty column label map")

        with open(csv_path, "r") as f:
            for row in csv.DictReader(f):
                timestamp = row[self.timestamp_column]
                if (self.parse_timestamps):
                    timestamp = dateutil.parser.parse(timestamp).timestamp()
                try:
                    for (data_column, table) in self.column_table_map:
                        table.record(
                            row[data_column], timestamp = timestamp,
                            append_location_data = append_location_data
                        )
                except TypeError:
                    print("no data exists for timestamp %s" % timestamp)
        self.db.commit()

class Dylos(CsvImporter):
    def __init__(self, *args, **kwargs):
        """ Initialize CsvImporter subclass that imports Dylos data """

        CsvImporter.__init__(self, *args, **kwargs)
        self.set_data_column("SMALLPARTICLES", "dylos smallparticles")
        self.set_data_column("LARGEPARTICLES", "dylos largeparticles")

class ADXL345(CsvImporter):
    def __init__(self, *args, **kwargs):
        """ Initialize CsvImporter subclass that imports ADXL345 data """

        CsvImporter.__init__(self, *args, **kwargs)
        self.set_data_column("X", "adxl345 x axis raw")
        self.set_data_column("Y", "adxl345 y axis raw")
        self.set_data_column("Z", "adxl345 z axis raw")

class HOBOU12(CsvImporter):
    def __init__(self, *args, **kwargs):
        """ Initialize CsvImporter subclass that imports HOBO U-12 data """

        CsvImporter.__init__(self, *args, **kwargs)
        self.set_data_column(
            "Temp, °F (LGR S/N: 20311528, SEN S/N: 20311528)", "hobo temp fahrenheit"
        )
        self.set_data_column(
            "RH, % (LGR S/N: 20311528, SEN S/N: 20311528)", "hobo relative humidity"
        )
        self.set_data_column(
            "Intensity, lum/ft² (LGR S/N: 20311528, SEN S/N: 20311528)", "hobo light intensity lum ft2"
        )

    def import_csv(self, csv_path):
        """ Overwrite CsvImporter.import_csv: The first line of HOBO U-12 CSV
        files must be ignored and the timestamp column name is specialy
        formatted
        """

        if (len(self.column_table_map) == 0):
            raise Exception("empty column label map")

        with open(csv_path, "r") as f:
            _ = f.readline()
            reader = csv.DictReader(f)

            for column in reader.fieldnames:
                if ("Date Time" in column):
                    self.set_timestamp_column(column)
                    break

            for row in reader:
                timestamp = dateutil.parser.parse(row[self.timestamp_column]).timestamp()
                try:
                    for (data_column, table) in self.column_table_map:
                        data = row[data_column]
                        if (not len(data) == 0):
                            table.record(data, timestamp = timestamp)
                except TypeError:
                    print("no data exists for timestamp %s" % timestamp)
        self.db.commit()

if (__name__ == "__main__"):
    #Dylos().import_csv(sys.argv[1])
    #ADXL345().import_csv(sys.argv[1])
    HOBOU12().import_csv(sys.argv[1])
