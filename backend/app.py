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
    originCoordinates, coopLocations = getCoopLocations(location, time_filter=False)
    body = {"coordinates": [originCoordinates.get("Longitude"),originCoordinates.get("Latitude")]}
    coopList = []
    for coop in coopLocations:
        coopList.append({**body, **coop})
    return jsonify(coopList)

@app.route('/routeing', methods=['GET'])
def routeing():
    routingProfile = request.args.get('routingprofile')
    location = request.args.get('location')
    originCoordinates, coopLocations = getCoopLocations(location, time_filter=False)
    calculationDatas = getAllRoutes(routingProfile, coopLocations, originCoordinates)
    return jsonify(calculationDatas)

if __name__ == '__main__':
    app.run()