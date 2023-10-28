#!/bin/python3
from flask import Flask, jsonify
from coop_locations import getCoopLocations
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/locations')

def locations():
        coopData = getCoopLocations("Basel", 10)
        return jsonify(coopData)
