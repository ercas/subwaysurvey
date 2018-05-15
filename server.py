#!/usr/bin/env python3

import flask
import os
import webbrowser

from db import DB

PORT = 8889

app = flask.Flask(__name__)

@app.route("/", methods = ["GET"])
def index():
    with open("./index.html", "r") as f:
        return f.read()

@app.route("/new_observation", methods = ["POST"])
def new_observation():
    form = flask.request.form
    if (form):
        notes = form.get("notes")
        if (len(notes) == 0):
            notes = None

        observation = (
            form.get("source_name"), form.get("location_name"),
            form.get("value"), notes
        )

        for field in range(3):
            if (len(observation[field]) == 0):
                return flask.jsonify(False)

        print(observation)

        db = DB()
        db.record(*observation)
        db.commit()
        return flask.jsonify(True)
    else:
        return flask.jsonify(False)

if (__name__ == "__main__"):
    webbrowser.open_new_tab("http://localhost:%d" % PORT)
    app.run(port = PORT, debug = False)
