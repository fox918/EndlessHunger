#!/bin/python3
from flask import Flask, jsonify
from CoopLocations import getCoopLocations

app = Flask(__name__)


@app.route('/locations')
def locations():
        coopData = getCoopLocations("Basel", 10)
        return jsonify(coopData)
