#!/usr/bin/env python3

import flask
import os
import webbrowser

from db import TStationDB

PORT = 8889

app = flask.Flask(__name__)

@app.route("/", methods = ["GET"])
def index():
    with open("./index.html", "r") as f:
        return f.read()

@app.route("/update_location", methods = ["POST"])
def new_observation():
    form = flask.request.form
    if (form):
        observation = (
            form.get("location_name"), form.get("status")
        )

        for field in observation:
            if (len(observation) == 0):
                return flask.jsonify(False)

        print(observation)

        with TStationDB() as db:
            db.record_location(*observation)
        return flask.jsonify({"received": observation})
    else:
        return flask.jsonify(False)

if (__name__ == "__main__"):
    webbrowser.open_new_tab("http://localhost:%d" % PORT)
    app.run(port = PORT, debug = False)
