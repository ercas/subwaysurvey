#!/usr/bin/env python3

import csv
import flask
import glob

PORT = 8889
DATA_DIR = "./data/"

app = flask.Flask(__name__)

@app.route("/", methods = ["GET"])
def index():
    with open("./editor.html", "r", encoding = "utf-8") as f:
        return f.read()

@app.route("/data/<day>/<sensor>")
def fetchData(day, sensor):
    joined_rows = []
    first = True
    for part in sorted(glob.glob("%s/%s/%s*.csv" % (DATA_DIR, day, sensor))):
        print("reading %s" % part)
        with open(part, "r") as f:
            if (not first):
                _ = f.readline()
            first = False
            joined_rows += f.readlines()
    return "".join(joined_rows)

if (__name__ == "__main__"):
    app.run(port = PORT, debug = False)