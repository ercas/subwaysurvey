#!/usr/bin/env python3

import csv
import flask
import glob
import os

PORT = 8889
DATA_DIR = "./data/"

app = flask.Flask(__name__)

@app.route("/", methods = ["GET"])
def index():
    with open("./editor.html", "r", encoding = "utf-8") as f:
        return f.read()

@app.route("/data/")
def showAvailableData():
    return flask.jsonify(os.listdir(DATA_DIR))

@app.route("/data/<day>/")
def showAvailableSesors(day):
    return flask.jsonify(os.listdir("%s/%s" % (DATA_DIR, day)))


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
            for line in f:
                if (len(line.rstrip()) > 0):
                    joined_rows.append(line)
    return "".join(joined_rows)

if (__name__ == "__main__"):
    app.run(port = PORT, debug = False)
