import csv
import requests
import os
from datetime import datetime, timedelta

def geocode_address(address):
    """Convert address to coordinates using ArcGIS"""
    try:
        url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
        params = {
            'f': 'json',
            'singleLine': address,
            'outFields': 'Match_addr,Addr_type',
            'maxLocations': 1
        }
        response = requests.get(url, params=params).json()
        
        if response.get('candidates') and len(response['candidates']) > 0:
            location = response['candidates'][0]['location']
            return (location['y'], location['x'])  # ArcGIS returns (lat, lon) as (y, x)
        
        return None
    except Exception as e:
        print(f"Geocoding failed for {address}: {e}")
        return None

def get_drive_time(start_coords, end_coords):
    """Get drive time using OSRM"""
    try:
        start_lon, start_lat = start_coords[1], start_coords[0]
        end_lon, end_lat = end_coords[1], end_coords[0]
        
        url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=false"
        response = requests.get(url).json()
        
        if response.get('code') == 'Ok':
            duration = response['routes'][0]['duration']  # in seconds
            distance = response['routes'][0]['distance']  # in meters
            return {
                'duration_mins': round(duration / 60, 1),
                'distance_miles': round(distance / 1609.34, 1)
            }
        return None
    except Exception as e:
        print(f"Routing failed: {e}")
        return None

def calculate_free_drive_times(input_csv, output_csv):
    # Check if output file already exists
    existing_data = {}
    if os.path.exists(output_csv):
        with open(output_csv, mode='r') as existing_file:
            reader = csv.DictReader(existing_file)
            for row in reader:
                # Use a unique identifier for each property (address in this case)
                address_key = f"{row['Street']}, {row['City']}, {row['State']} {row['ZIP Code']}"
                existing_data[address_key] = {
                    'Coordinates': row.get('Coordinates', ''),
                    'Drive Time (mins)': row.get('Drive Time (mins)', ''),
                    'Distance (miles)': row.get('Distance (miles)', '')
                }
    
    # Geocode the destination once
    destination = "781 Lasalle St, New Orleans, LA 70112"
    dest_coords = geocode_address(destination)
    
    if not dest_coords:
        print("Failed to geocode destination address")
        return
    
    with open(input_csv, mode='r') as infile, open(output_csv, mode='w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Coordinates', 'Drive Time (mins)', 'Distance (miles)']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            # Construct the full address from separate components
            origin = f"{row['Street']}, {row['City']}, {row['State']} {row['ZIP Code']}"
            address_key = origin
            
            # Check if we have existing data for this property
            if address_key in existing_data and existing_data[address_key]['Coordinates']:
                existing_row = existing_data[address_key]
                if (existing_row['Drive Time (mins)'] and 
                    existing_row['Drive Time (mins)'] not in ["Geocoding failed", "Routing failed"] and
                    existing_row['Distance (miles)'] and 
                    existing_row['Distance (miles)'] not in ["Geocoding failed", "Routing failed"]):
                    
                    # Use existing data
                    row['Coordinates'] = existing_row['Coordinates']
                    row['Drive Time (mins)'] = existing_row['Drive Time (mins)']
                    row['Distance (miles)'] = existing_row['Distance (miles)']
                    writer.writerow(row)
                    continue
            
            # If no existing data or data was invalid, process new request
            origin_coords = geocode_address(origin)
            
            if origin_coords:
                row['Coordinates'] = f"{origin_coords[0]}, {origin_coords[1]}"
                route = get_drive_time(origin_coords, dest_coords)
                if route:
                    row['Drive Time (mins)'] = f"{route['duration_mins']}"
                    row['Distance (miles)'] = f"{route['distance_miles']}"
                else:
                    row['Drive Time (mins)'] = "Routing failed"
                    row['Distance (miles)'] = "Routing failed"
            else:
                row['Coordinates'] = "Geocoding failed"
                row['Drive Time (mins)'] = "Geocoding failed"
                row['Distance (miles)'] = "Geocoding failed"
            
            writer.writerow(row)

if __name__ == "__main__":
    input_filename = "1_properties.csv"
    output_filename = "2_properties_w_drive.csv"
    calculate_free_drive_times(input_filename, output_filename)
    print(f"Drive time calculations complete. Results saved to {output_filename}")