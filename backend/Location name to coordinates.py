import requests
from geopy.geocoders import Nominatim
import json
from datetime import datetime

# Set the number of nearby Coop locations to retrieve
numNearbyCoop = 10

def getCoopLocations(villageName):
    geolocator = Nominatim(user_agent="CoopFinder")
    location = geolocator.geocode(f'{villageName}, Switzerland')
    if location is None:
        print(f'No location found for {villageName}, Switzerland')
        return
    lat, lng = location.latitude, location.longitude
    print(f'Coordinates: ({lat}, {lng})')

    url = f"https://www.coop.ch/de/unternehmen/standorte-und-oeffnungszeiten.getvstlist.json?lat={lat}&lng={lng}&start=1&end={numNearbyCoop}&filterFormat=+&filterAttribute=&filterOpen=false&gasIndex=0"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f'Failed to retrieve data: {e}')
        return

    try:
        responseJson = response.json()
    except json.JSONDecodeError as e:
        print(f'Failed to decode JSON: {e}')
        return

    coopLocations = []
    openCoopsCount = 0
    for coopLocation in responseJson.get('vstList', []):
        name = coopLocation.get('namePublic')
        distance = int(coopLocation.get('distance'))
        logoUrl = coopLocation.get('logo')
        formatId = coopLocation.get('formatId', '').capitalize()
        if formatId.lower() == 'id':
            formatId = 'Interdiscount'
        zipCode = coopLocation.get('plz')
        villageName = coopLocation.get('ort')
        streetName = coopLocation.get('strasse')
        houseNumber = coopLocation.get('hausnummer')

        # Determine the opening and closing times
        now = datetime.now()
        currentDay = now.strftime("%A").upper()
        openingTime, closingTime = None, None
        for openingHours in coopLocation.get('openingHours', []):
            if openingHours['day'] == currentDay:
                timeRange = openingHours['time'].split(' - ')
                if len(timeRange) == 2:
                    openingTime, closingTime = timeRange
                    break

        openStatus = openingTime is not None and closingTime is not None

        if openStatus:
            openCoopsCount += 1

        coopLocations.append({
            'Name': name,
            'Distance': distance,
            'LogoUrl': logoUrl,
            'FormatId': formatId,
            'ZipCode': zipCode,
            'VillageName': villageName,
            'StreetName': streetName,
            'HouseNumber': houseNumber,
            'Open': openStatus,
            'OpeningTime': openingTime,
            'ClosingTime': closingTime
        })

    print(f'Number of open Coop locations: {openCoopsCount}')

    # Write the data to a JSON file
    outputPath = 'coopLocations.json'
    try:
        with open(outputPath, 'w', encoding='utf-8') as f:
            json.dump(coopLocations, f, ensure_ascii=False, indent=4)
        print(f'Data written to {outputPath}')
    except Exception as e:
        print(f'Failed to write data to {outputPath}: {e}')

# Usage
villageName = input("Enter the name of a village, city or address in Switzerland: ")
getCoopLocations(villageName)
