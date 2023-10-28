import requests
from geopy.geocoders import Nominatim
import json
from datetime import datetime


def get_unique_format_ids(lat, lng, numCoops):
    url = f"https://www.coop.ch/de/unternehmen/standorte-und-oeffnungszeiten.getvstlist.json?lat={lat}&lng={lng}&start=1&end={numCoops}&filterFormat=+&filterAttribute=&filterOpen=false&gasIndex=0"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f'Failed to retrieve data: {e}')
        return

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print(f'Failed to decode JSON: {e}')
        return

    format_ids = set()
    for coopLocation in data.get('vstList', []):
        format_id = coopLocation.get('formatId')
        if format_id:
            format_ids.add(format_id)

    # Save the unique format IDs to a file
    with open('coop_formats.txt', 'w') as file:
        for format_id in format_ids:
            file.write(f'{format_id}\n')

    print(f'Unique format IDs saved to coop_formats.txt')

# # Usage:
# lat = 47.543427  # Replace with the desired latitude
# lng = 7.598133599999983  # Replace with the desired longitude
# numCoops = 2233  # Replace with the desired number of Coop locations

# get_unique_format_ids(lat, lng, numCoops)





def getCoopLocations(locationName, numCoops):
    def get_food_offering_formats():
        """Load the list of format IDs that offer food."""
        with open('food_offering_formats.txt', 'r', encoding='ISO-8859-1') as file:
            formats = set(line.strip().lower() for line in file)
        return formats

    food_offering_formats = get_food_offering_formats()

    geolocator = Nominatim(user_agent="CoopFinder")
    location = geolocator.geocode(f'{locationName}, Switzerland')
    if location is None:
        print(f'No location found for {locationName}, Switzerland')
        return
    lat, lng = location.latitude, location.longitude
    print(f'Coordinates: ({lat}, {lng})')

    url = f"https://www.coop.ch/de/unternehmen/standorte-und-oeffnungszeiten.getvstlist.json?lat={lat}&lng={lng}&start=1&end={numCoops}&filterFormat=+&filterAttribute=&filterOpen=false&gasIndex=0"

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
        formatId = coopLocation.get('formatId', '').lower()  # Get the formatId in lowercase

        # Debugging print
        if formatId not in food_offering_formats:
            print(f"Filtered out {formatId} for {coopLocation.get('namePublic')}")
            continue

        name = coopLocation.get('namePublic')
        distance = int(coopLocation.get('distance'))
        logoUrl = coopLocation.get('logo')
        zipCode = coopLocation.get('plz')
        cityName = coopLocation.get('ort')
        streetName = coopLocation.get('strasse')
        houseNumber = coopLocation.get('hausnummer')
        latitude = coopLocation.get('geoKoordinaten', {}).get('latitude')
        longitude = coopLocation.get('geoKoordinaten', {}).get('longitude')

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
            'CityName': cityName,
            'StreetName': streetName,
            'HouseNumber': houseNumber,
            'Latitude': latitude,
            'Longitude': longitude,
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

    return coopLocations


getCoopLocations("Basel", 10)


# Usage
# locationName = input("Enter the name of a village, city or address in Switzerland: ")
# numCoops = int(input("Enter the number of Coop locations to retrieve: "))
# getCoopLocations(locationName, numCoops)
