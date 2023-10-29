#!/bin/python3
from flask import Flask, jsonify, request
from coop_locations import getCoopLocations
from getRoutes import getAllRoutes
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/locations')

def locations():
    coopData = getCoopLocations("Basel")
    return jsonify(coopData)
    
@app.route('/calculations', methods=['GET'])
def calculations():
    location = request.args.get('location')
    filter_value = request.args.get('filter')
    originCoordinates, coopLocations = getCoopLocations(location, time_filter=False)
    # calculationDatas = getAllRoutes("driving-car", coopLocations, originCoordinates)
    body = {"coordinates": [[originCoordinates.get("Longitude"),originCoordinates.get("Latitude")]]}
    return jsonify({**body, **coopLocations})

@app.route('/routeing', methods=['GET'])
def calculations():
    routingProfile = request.args.get('routingprofile')
    location = request.args.get('location')
    filter_value = request.args.get('filter')
    originCoordinates, coopLocations = getCoopLocations(location, time_filter=False)
    calculationDatas = getAllRoutes("driving-car", coopLocations, originCoordinates)
    return jsonify(calculationDatas)

if __name__ == '__main__':
    app.run()