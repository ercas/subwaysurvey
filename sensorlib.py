#!/usr/bin/env python3

import dateutil
import pandas

HOBO_DROP_COLUMNS = ["Host Connected", "Stopped", "End Of File"]

class Locations(object):

    def __init__(self, locations_csv, location_timestamp_column = "TIMESTAMP"):
        """ Initialize Locations object to simplify the task of finding where
        the sensors were in a point in time

        :param str locations_csv: The path of the CSV file storing locations
            (this would have been generated by server.py)
        :param str location_timestamp_column: The column of the CSV file containing
            location timestamps, in seconds
        """

        self.locations = pandas.read_csv(locations_csv)
        self.location_timestamp_column = location_timestamp_column
        self.blank_row = pandas.Series([None] * len(self.locations.columns))

    def get_location(self, timestamp):
        """ Get the location of the sensors at a point in time

        The location is determined by finding the last recorded location since
        the given timestamp

        :param float timestamp: The Unix time to look up
        :returns: A Pandas Series object containing location information for
            the given timestamp, pulled from the locations csv file
        :rtype: pandas.core.series.Series
        """

        rows_before = self.locations[
            self.locations[self.location_timestamp_column] < timestamp
        ]
        if (len(rows_before) == 0):
            return self.blank_row
        else:
            return rows_before.iloc[-1]

    def join_locations(self, df, timestamp_column = "TIME", drop_no_location = True):
        """ Wrapper for get_location that merges the input and results into a
        new dataframe

        :param pandas.core.frame.DataFrame df: The dataframe to be joined with
            location data
        :param timestamp_column str: The column of the dataframe containing
            timestamps in seconds
        :param bool drop_no_location: Drop rows with no location info
        :returns: A new DataFrame
        :rtype: pandas.core.frame.DataFrame
        """

        matched_locations = df[timestamp_column].apply(self.get_location).dropna(axis = 1, how = "all")
        # FIXME
        #del matched_locations[self.location_timestamp_column]
        merged = df.merge(
            matched_locations,
            left_index = True, right_index = True
        )
        if (drop_no_location):
            return merged.dropna(subset = self.locations.columns)
        else:
            return merged

def read_hobo_csv(hobo_csv):
    """ Wrapper for reading CSV files outputted by the HOBO U12 data logger """
    with open(hobo_csv, "r") as f:
        _ = f.readline()
        df = pandas.read_csv(f)
        timestamp_column = None

        del df["#"]

        for column_name in df.columns:
            for drop_column in HOBO_DROP_COLUMNS:
                if (drop_column in column_name):
                    del df[column_name]
                elif ("Date Time" in column_name):
                    timestamp_column = column_name

        #df["TIME"] = pandas.to_datetime(df.pop(timestamp_column)).apply(lambda x: x.timestamp())
        df["TIME"] = df.pop(timestamp_column).apply(lambda x: dateutil.parser.parse(x).timestamp())
        return df
