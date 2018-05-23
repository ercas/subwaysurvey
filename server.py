#!/usr/bin/env python3

import flask
import os
import webbrowser

from db import TStationDB

PORT = 8889

app = flask.Flask(__name__)

@app.route("/", methods = ["GET"])
def index():
    with open("./index.html", "r", encoding = "utf-8") as f:
        return f.read()

@app.route("/update_location", methods = ["POST"])
def update_location():
    form = flask.request.form
    if (form):
        location = (
            form.get("location_name"), form.get("position_name"), form.get("status")
        )

        for field in location:
            if (len(field) == 0):
                return flask.jsonify({"error": "blank field in input"})

        print(location)

        with TStationDB() as db:
            db.record_location(*location)

        return flask.jsonify({
            "received": {
                "location": location
            }
        })
    else:
        return flask.jsonify({"error": "blank form"})

@app.route("/new_observation", methods = ["POST"])
def new_observation():
    form = flask.request.form
    if (form):
        observation = (
            form.get("sensor"), form.get("value")
        )
        notes = form.get("notes")

        if (len(notes) == 0):
            notes = None

        for field in observation:
            if (len(field) == 0):
                return flask.jsonify({"error": "blank field in input"})

        print(observation, notes)

        with TStationDB() as db:
            db.record(*observation, notes = notes)

        return flask.jsonify({
            "received": {
                "observation": observation,
                "notes": notes
            }
            })
    else:
        return flask.jsonify({"error": "blank form"})

if (__name__ == "__main__"):
    webbrowser.open_new_tab("http://localhost:%d" % PORT)
    app.run(port = PORT, debug = False)
