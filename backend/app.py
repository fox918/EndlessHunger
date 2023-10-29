#!/bin/python3
from flask import Flask, jsonify, request
from coop_locations import getCoopLocations
from getRoutes import getAllRoutes
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/locations')

def locations():
    coopData = getCoopLocations("Basel", 10)
    return jsonify(coopData)

    
# @app.route('/route/<variable1>/<variable2>')
# def route(variable1, variable2):
#     # variable1 und variable2 sind die empfangenen URL-Parameter
#     return f'Variable 1: {variable1}, Variable 2: {variable2}'

# @app.route('/search/<searchstring>', methods=['GET'])
   
# def serach(searchstring):
#         originCoordinates, coopLocations = getCoopLocations(searchstring, 10, time_filter=False)
#         calculationDatas = getAllRoutes("driving-car", coopLocations)
#         return jsonify(calculationDatas)
    
@app.route('/calculations', methods=['GET'])
def calculations():
    # location = request.args.get('location')
    # filter_value = request.args.get('filter')
    # originCoordinates, coopLocations = getCoopLocations(location, 10, time_filter=False)
    # calculationDatas = getAllRoutes("driving-car", coopLocations)
    # return jsonify(calculationDatas)
    location = request.args.get('location')
    filter_value = request.args.get('filter')

    return f'Location: {location}, Filter: {filter_value}'

if __name__ == '__main__':
    app.run()