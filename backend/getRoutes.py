import requests
import json
import time
import os
from dotenv import load_dotenv
import xml.etree.ElementTree as ET# Constructing the XML elements and attributes
from coop_locations import getCoopLocations
from concurrent.futures import ThreadPoolExecutor

def getRoute(coopLocations, routingProfile, originCoordinates):
    longitude = coopLocations.get("Longitude")
    latitude = coopLocations.get("Latitude")
    body = {"coordinates": [[originCoordinates.get("Longitude"),originCoordinates.get("Latitude")], [longitude, latitude]]}
    
    load_dotenv()
    authorization = os.getenv("authorization")
    
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': authorization,
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

def getAllRoutes(routingProfile, coopLocations,originCoordinates):

    if routingProfile == "publicTransport":
        
        pass

    elif routingProfile == "driving-car" or routingProfile == "cycling-regular" or routingProfile == "foot-walking" or routingProfile == "wheelchair":

        # routes = list(map(lambda x: getRoute(x, routingProfile,originCoordinates), coopLocations))
        routes = []
        with ThreadPoolExecutor(max_workers=5) as executor:  # Du kannst die Anzahl der parallelen Threads anpassen
            futures = [executor.submit(getRoute, x, routingProfile, originCoordinates) for x in coopLocations]
            for future in futures:
                time.sleep(0.1)
                result = future.result()
                if result:
                    routes.append(result)
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
        
def getBestRoute(routingProfile, coopLocations,originCoordinates):
    getAllRoutes(routingProfile, coopLocations, originCoordinates)

if __name__ == '__main__':
    originCoordinates, coopLocations = getCoopLocations("Basel", time_filter=False)
    ans = getAllRoutes("driving-car", coopLocations, originCoordinates)