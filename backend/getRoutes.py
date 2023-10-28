import requests
import json
import xml.etree.ElementTree as ET# Constructing the XML elements and attributes
from coop_locations import getCoopLocations

coopLocations = getCoopLocations("Basel", 10)

def getRoute(coopLocations, routing_profile):
    longitude = coopLocations.get("Longitude")
    latitude = coopLocations.get("Latitude")
    body = {"coordinates": [[8.681495, 49.41461], [longitude, latitude]]}
    
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': '5b3ce3597851110001cf6248bf3d9d3adcf5443db7ee91adc2489f2d',
        'Content-Type': 'application/json; charset=utf-8'
    }
    # Use the routing profile variable in the URL
    
    url = f'http://api.openrouteservice.org/v2/directions/{routing_profile}/geojson'

    call = requests.post(url, json=body, headers=headers)


    if call.status_code == 200:
        response_json = json.loads(call.text)  # Parse the JSON response
        print("Route calculated")
        return response_json
    else:
        print("Request was not successful. Status code:", call.status_code)


def getAllRoutes(routing_profile, coopLocations):

    if routing_profile == "publicTransport":
        
        pass

    elif routing_profile == "driving-car" or routing_profile == "cycling-regular" or routing_profile == "foot-walking" or routing_profile == "wheelchair":

        routes = list(map(lambda x: getRoute(x, routing_profile), coopLocations))

        with open('routes.json', 'w') as json_file:
            json.dump(routes, json_file, indent=4)  # Save the JSON to a file with indentation
        print ("Routes saved")

        sortedRoutes = sorted(routes, key=lambda x: x['features'][0]['properties']['summary']['distance'])

        with open('sortedRoutes.json', 'w') as json_file:
            json.dump(sortedRoutes, json_file, indent=4)  # Save the JSON to a file with indentation
        print ("sortedRoutes saved")

        return sortedRoutes

    else:
        print("Wrong Routing Profile", routing_profile)

getAllRoutes("driving-car", coopLocations)