#!/usr/bin/env python3

import flask
import os
import webbrowser

from db import TStationDB

PORT = 8889

app = flask.Flask(__name__)

def sanity_check_pretty_print(reason, old_value_str, new_value_str):
    print("%s: \"%s\" -> \"%s\"")

def sanity_check(sensor_name, value_str):
    """ Perform sanity checks after auto corrections if possible """
    value_float = float(value_str)

    if (sensor_name == "3m sd200 slm"):

        # stated range of 3m sd-200 slm is 40 to 130 dB
        if (value_float > 130):
            first_zero_loc = value_str.find("0")

            if (not "." in value_str):
                # possibility: user entered "0" instead of a decimal point
                if (first_zero_loc != -1):
                    new_value_str = value_str[:first_zero_loc] + "." + value_str[(first_zero_loc + 1):]
                    sanity_check_pretty_print(
                        "converted \"0\" -> \".\"",
                        value_str,
                        new_value_str
                    )
                    return sanity_check(sensor_name, new_value_str)

                # possibility: user did not enter decimal point. the 3m sd-200
                # slm has one decimal point so we add the decimal point between
                # the last and second to last characters
                else:
                    new_value_str = value_str[:-1] + "." + value_str[-1]
                    sanity_check_pretty_print(
                        "inserted decimal point",
                        value_str,
                        new_value_str
                    )
                    return sanity_check(sensor_name, new_value_str)
            else:
                return False

        elif (value_float < 40):
            return False

    return value_float

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
