#!/bin/python3
from flask import Flask, jsonify
from coop_locations import getCoopLocations
from getRoutes import getAllRoutes
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/locations')

def locations():
        coopData = getCoopLocations("Basel", 10)
        return jsonify(coopData)


@app.route('/calculations')

def calculations():
        calculationDatas = getAllRoutes("driving-car", getCoopLocations("Basel", 10))
        return jsonify(calculationDatas)