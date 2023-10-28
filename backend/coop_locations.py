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





def getCoopLocations(locationName, search_radius=10):
    
    def get_food_offering_formats():
        """Load the list of format IDs that offer food."""
        with open('food_offering_formats.txt', 'r', encoding='ISO-8859-1') as file:
            formats = set(line.strip().lower() for line in file)
        return formats

    def fetch_coop_data(url):
        """Fetch Coop data from the given URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            print(f"Fetched {len(response.json().get('vstList', []))} Coop locations.")
            return response.json()
        except requests.RequestException as e:
            print(f'Failed to retrieve data: {e}')
            return None

    def is_open_now(coop):
        """Check if the coop is open right now."""
        now = datetime.now()
        currentDay = now.strftime("%A").upper()
        openingTime, closingTime = None, None
        for openingHours in coop.get('openingHours', []):
            if openingHours['day'] == currentDay:
                timeRange = openingHours['time'].split(' - ')
                if len(timeRange) == 2:
                    openingTime, closingTime = timeRange
                    break
        current_time_str = now.strftime('%H:%M')
        return openingTime, closingTime, openingTime is not None and closingTime is not None and openingTime <= current_time_str <= closingTime

    def filter_coops(coops, food_offering_formats):
        """Filter coops based on criteria."""
        qualified_coops = []
        for coop in coops:
            formatId = coop.get('formatId', '').lower()
            distance_in_km = int(coop.get('distance')) / 1000
            if formatId in food_offering_formats and distance_in_km <= search_radius:
                openingTime, closingTime, openStatus = is_open_now(coop)
                if openStatus:
                    coop_json = create_json(coop, openingTime, closingTime, openStatus)
                    qualified_coops.append(coop_json)
            if len(qualified_coops) >= 10 or distance_in_km > search_radius:
                break
        
        print(f"Filtered {len(qualified_coops)} Coop locations that match the criteria.")
        return qualified_coops

    def create_json(coop, openingTime, closingTime, openStatus):
        """Create a JSON representation of a coop."""
        return {
            'Name': coop.get('namePublic'),
            'Distance': int(coop.get('distance')),
            'FormatId': coop.get('formatId', '').lower(),
            'Latitude': coop.get('geoKoordinaten', {}).get('latitude'),
            'Longitude': coop.get('geoKoordinaten', {}).get('longitude'),
            'LogoUrl': coop.get('logo'),
            'ZipCode': coop.get('plz'),
            'CityName': coop.get('ort'),
            'StreetName': coop.get('strasse'),
            'HouseNumber': coop.get('hausnummer'),
            'Open': openStatus,
            'OpeningTime': openingTime,
            'ClosingTime': closingTime
        }

    # Main logic of getCoopLocations
    food_offering_formats = get_food_offering_formats()

    geolocator = Nominatim(user_agent="CoopFinder")
    location = geolocator.geocode(f'{locationName}, Switzerland')
    if location is None:
        print(f'No location found for {locationName}, Switzerland')
        return []
    lat, lng = location.latitude, location.longitude
    print(f'Coordinates: ({lat}, {lng})')

    fetch_count = 100  # Fetch a larger number in a single call
    url = f"https://www.coop.ch/de/unternehmen/standorte-und-oeffnungszeiten.getvstlist.json?lat={lat}&lng={lng}&start=1&end={fetch_count}&filterFormat=+&filterAttribute=&filterOpen=false&gasIndex=0"
    coops_data = fetch_coop_data(url)
    if not coops_data:
        return []

    qualified_coops = filter_coops(coops_data.get('vstList', []), food_offering_formats)
    print(qualified_coops)
    return qualified_coops

getCoopLocations("Basel")



# Usage
# locationName = input("Enter the name of a village, city or address in Switzerland: ")
# numCoops = int(input("Enter the number of Coop locations to retrieve: "))
# getCoopLocations(locationName, numCoops)
