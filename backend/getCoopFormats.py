# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 16:41:32 2023

@author: timse
"""

import requests
import json


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

# Usage:
lat = 47.543427  # Replace with the desired latitude
lng = 7.598133599999983  # Replace with the desired longitude
numCoops = 2233  # Replace with the desired number of Coop locations

get_unique_format_ids(lat, lng, numCoops)