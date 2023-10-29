import requests
import json
import xml.etree.ElementTree as ET# Constructing the XML elements and attributes
from coop_locations import getCoopLocations
import numpy as np
import pandas as pd
import traceback

def get_closest_stops(file_path, start_coords, end_coords):
    """
    Returns the BPUIC values and coordinates for the closest stops to the start and end coordinates.    Parameters:
    - file_path: Path to the CSV file containing public transport stop data.
    - start_coords: Tuple of (latitude, longitude) for the start location.
    - end_coords: Tuple of (latitude, longitude) for the end location.    Returns:
    - Tuple of (BPUIC value, (latitude, longitude)) for the closest stops to the start and end coordinates.
    """
    try:
        # Load the data from the file
        df = pd.read_csv(file_path, delimiter=";", encoding="ISO-8859-1", skiprows=6)        # Calculate the Euclidean distance for the start and end coordinates
        df['distance_to_start'] = np.sqrt((df['N_WGS84'] - start_coords[0])**2 + (df['E_WGS84'] - start_coords[1])**2)
        df['distance_to_end'] = np.sqrt((df['N_WGS84'] - end_coords[0])**2 + (df['E_WGS84'] - end_coords[1])**2)        # Get the BPUIC values and coordinates for the closest stops
        start_row = df.loc[df['distance_to_start'].idxmin()]
        end_row = df.loc[df['distance_to_end'].idxmin()]
        start_data = (start_row['BPUIC'], start_row['BEZEICHNUNG_OFFIZIELL'], start_row['N_WGS84'], start_row['E_WGS84'])
        end_data = (end_row['BPUIC'], end_row['BEZEICHNUNG_OFFIZIELL'], end_row['N_WGS84'], end_row['E_WGS84'])
        return start_data, end_data
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        traceback.print_exc()
        return None, None# Test the safer function with sample coordinates

def getRoute(coopLocations, routingProfile, originCoordinates):
    longitude = coopLocations.get("Longitude")
    latitude = coopLocations.get("Latitude")
    body = {"coordinates": [[originCoordinates.get("Longitude"),originCoordinates.get("Latitude")], [longitude, latitude]]}
    
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': '5b3ce3597851110001cf6248bf3d9d3adcf5443db7ee91adc2489f2d',
        'Content-Type': 'application/json; charset=utf-8'
    }
    # Use the routing profile variable in the URL
    
    url = f'http://api.openrouteservice.org/v2/directions/{routingProfile}/geojson'

    call = requests.post(url, json=body, headers=headers)


    if call.status_code == 200:
        route = json.loads(call.text)  # Parse the JSON response
        print("Route calculated")

        coop = {**body, **coopLocations, **route}

        return coop
    else:
        print("Request was not successful. Status code:", call.status_code)

def getPublicTransportRoute(coopLocations, routingProfile, originCoordinates):
    longitudeOrigin = originCoordinates.get("Longitude")
    latitudeOrigin = originCoordinates.get("Latitude")
    originCoordinates = [latitudeOrigin, longitudeOrigin]

    longitudeCoop = coopLocations.get("Longitude")
    latitudeCoop = coopLocations.get("Latitude")
    endCoordinates = [latitudeCoop, longitudeCoop]

    print(originCoordinates)
    print(endCoordinates)
    originPtStop, coopPtStop = get_closest_stops('dienststellen_actualdate.csv', originCoordinates, endCoordinates)

    print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
    print(originPtStop)
    print(coopPtStop)

    coordiantesInfo = {"coordinates": [[longitudeOrigin, latitudeOrigin], [longitudeCoop, latitudeCoop]]}
    publicTransportInfo = {"coordinates": [[originPtStop[1], originPtStop[3], originPtStop[2]], [coopPtStop[1], coopPtStop[3], coopPtStop[2]]]}

    body = {"coordinates": [[longitudeOrigin, latitudeOrigin], [originPtStop[3], originPtStop[2]], [coopPtStop[3], coopPtStop[2]], [longitudeCoop, latitudeCoop]]}
    #body = {"coordinates": [[longitudeOrigin, latitudeOrigin], [longitudeCoop, latitudeCoop]]}

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': '5b3ce3597851110001cf6248bf3d9d3adcf5443db7ee91adc2489f2d',
        'Content-Type': 'application/json; charset=utf-8'
    }
    # Use the routing profile variable in the URL
    
    url = f'http://api.openrouteservice.org/v2/directions/foot-walking/geojson'

    call = requests.post(url, json=body, headers=headers)


    if call.status_code == 200:
        route = json.loads(call.text)  # Parse the JSON response
        print("Route calculated")

        coop = {**coordiantesInfo, **publicTransportInfo, **coopLocations, **route}

        return coop
    else:
        print("Request was not successful. Status code:", call.status_code)

def getAllRoutes(routingProfile, coopLocations, originCoordinates):

    if routingProfile == "public-transport":
        
        routes = list(map(lambda x: getPublicTransportRoute(x, routingProfile,originCoordinates), coopLocations))

        with open('routes.json', 'w') as json_file:
            json.dump(routes, json_file, indent=4)  # Save the JSON to a file with indentation
        print ("Routes saved")

        sortedRoutes = sorted(routes, key=lambda x: x['features'][0]['properties']['summary']['distance'])

        with open('sortedRoutes.json', 'w') as json_file:
            json.dump(sortedRoutes, json_file, indent=4)  # Save the JSON to a file with indentation
        print ("sortedRoutes saved")

        return sortedRoutes
        


    elif routingProfile == "driving-car" or routingProfile == "cycling-regular" or routingProfile == "foot-walking" or routingProfile == "wheelchair":

        routes = list(map(lambda x: getRoute(x, routingProfile,originCoordinates), coopLocations))

        with open('routes.json', 'w') as json_file:
            json.dump(routes, json_file, indent=4)  # Save the JSON to a file with indentation
        print ("Routes saved")

        sortedRoutes = sorted(routes, key=lambda x: x['features'][0]['properties']['summary']['distance'])

        with open('sortedRoutes.json', 'w') as json_file:
            json.dump(sortedRoutes, json_file, indent=4)  # Save the JSON to a file with indentation
        print ("sortedRoutes saved")

        return sortedRoutes

    else:
        print("Wrong Routing Profile", routingProfile)

if __name__ == '__main__':
    originCoordinates, coopLocations = getCoopLocations("Eptingen", 10, time_filter=False)
    ans = getAllRoutes("public-transport", coopLocations, originCoordinates)