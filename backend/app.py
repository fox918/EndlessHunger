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
        originCoordinates, coopLocations = getCoopLocations("Basel", 10, time_filter=False)
        calculationDatas = getAllRoutes("driving-car", coopLocations)
        return jsonify(calculationDatas)
    
@app.route('/search/<searchstring>')
   
def serach(searchstring):
        originCoordinates, coopLocations = getCoopLocations(searchstring, 10, time_filter=False)
        calculationDatas = getAllRoutes("driving-car", coopLocations)
        return jsonify(calculationDatas)