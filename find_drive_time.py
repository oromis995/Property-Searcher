import csv
import requests
from datetime import datetime, timedelta

def get_next_monday_8_20am():
    today = datetime.now()
    # If today is Monday and before 8:20am, use today
    if today.weekday() == 0 and today.time() < datetime.strptime("08:20", "%H:%M").time():
        return today.replace(hour=8, minute=20, second=0, microsecond=0)
    # Otherwise find next Monday
    days_ahead = (0 - today.weekday()) % 7  # 0 is Monday
    if days_ahead == 0:  # Today is Monday but after 8:20am
        days_ahead = 7
    next_monday = today + timedelta(days=days_ahead)
    return next_monday.replace(hour=8, minute=20, second=0, microsecond=0)

def geocode_address(address):
    """Convert address to coordinates using Nominatim"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json"
        headers = {'User-Agent': 'Mozilla/5.0'}  # Nominatim requires user agent
        response = requests.get(url, headers=headers).json()
        if response:
            return (float(response[0]['lat']), float(response[0]['lon']))
        
        # If first attempt fails, try replacing city with New Orleans
        parts = address.split(',')
        if len(parts) >= 2:
            new_address = parts[0].strip() + ", New Orleans, LA" + (',' + ','.join(parts[2:]) if len(parts) > 2 else '')
            url = f"https://nominatim.openstreetmap.org/search?q={new_address}&format=json"
            response = requests.get(url, headers=headers).json()
            if response:
                return (float(response[0]['lat']), float(response[0]['lon']))
        
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
            origin = row['Address']
            print("Processing: " + row['Address'])
            origin_coords = geocode_address(origin)
            
            if origin_coords:
                row['Coordinates'] = f"{origin_coords[0]}, {origin_coords[1]}"
                route = get_drive_time(origin_coords, dest_coords)
                if route:
                    row['Drive Time (mins)'] = f"{route['duration_mins']} mins"
                    row['Distance (miles)'] = f"{route['distance_miles']} miles"
                else:
                    row['Drive Time (mins)'] = "Routing failed"
                    row['Distance (miles)'] = "Routing failed"
            else:
                row['Coordinates'] = "Geocoding failed"
                row['Drive Time (mins)'] = "Geocoding failed"
                row['Distance (miles)'] = "Geocoding failed"
            
            writer.writerow(row)

if __name__ == "__main__":
    input_filename = "redfin_properties.csv"  # Replace with your input file name
    output_filename = "properties_with_drive_times.csv"
    calculate_free_drive_times(input_filename, output_filename)
    print(f"Drive time calculations complete. Results saved to {output_filename}")