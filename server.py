#!/usr/bin/env python3
# flask web server that serves web app front end and connects to database back
# end

import flask
import os
import webbrowser

from db import TStationDB
from sanity_check import sanity_check

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
        sensor = form.get("sensor")
        raw_value = form.get("value")

        if (len(sensor) == 0):
            return flask.jsonify({"error": "blank sensor"})

        elif (len(raw_value) == 0):
            return flask.jsonify({"error": "blank value"})

        else:
            notes = form.get("notes")
            if (len(notes) == 0):
                notes = None

            try:
                sane_value = sanity_check(sensor, raw_value)
            except Exception as err:
                return flask.jsonify({
                    "error": "sanity check failed",
                    "exception_text": str(err)
                })

            if (sane_value):
                print(sensor, raw_value, sane_value, notes)

                with TStationDB() as db:
                    db.record(sensor, sane_value, notes = notes)

                return flask.jsonify({
                    "received": {
                        "sensor": sensor,
                        "raw_value": raw_value,
                        "sane_value": sane_value,
                        "notes": notes
                    }
                })

            else:
                return flask.jsonify({"error": "sanity check and auto correction failed"})

    else:
        return flask.jsonify({"error": "blank form"})

if (__name__ == "__main__"):
    webbrowser.open_new_tab("http://localhost:%d" % PORT)
    app.run(port = PORT, debug = False)
