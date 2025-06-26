import pandas as pd
import requests
import time
import os

# Load CSV
df = pd.read_csv('2_properties_w_drive.csv')

# Check if previous output file exists
output_file = '3_properties_w_flood.csv'
previous_results = {}
if os.path.exists(output_file):
    try:
        previous_df = pd.read_csv(output_file)
        if 'Coordinates' in previous_df.columns and 'Flood Zone' in previous_df.columns:
            previous_results = dict(zip(previous_df['Coordinates'], previous_df['Flood Zone']))
            print(f"Loaded {len(previous_results)} previous flood zone results")
    except Exception as e:
        print(f"Could not read previous output file: {e}")

# FEMA NFHL FeatureServer (Flood Hazard Zones layer 28)
FEMA_URL = "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query"
           
def get_flood_zone(lat, lon):
    try:
        params = {
            'geometry': f'{lon},{lat}',
            'geometryType': 'esriGeometryPoint',
            'inSR': '4326',
            'spatialRel': 'esriSpatialRelIntersects',
            'outFields': 'FLD_ZONE,ZONE_SUBTY',
            'returnGeometry': 'false',
            'f': 'json'
        }
        response = requests.get(FEMA_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('features'):
            zone = data['features'][0]['attributes']
            return f"{zone.get('FLD_ZONE')} ({zone.get('ZONE_SUBTY', 'N/A')})"
        else:
            return "Not in mapped flood zone"
    except Exception as e:
        return f"Error: {e}"

# Loop over properties and query FEMA
flood_zones = []
total_queries = 0
new_queries = 0

for coord in df['Coordinates']:
    if coord in previous_results:
        # Use cached result
        flood_zones.append(previous_results[coord])
        total_queries += 0  # No new query needed
    elif isinstance(coord, str) and "," in coord:
        try:
            lat, lon = map(float, coord.strip().split(","))
            zone = get_flood_zone(lat, lon)
            flood_zones.append(zone)
            total_queries += 1
            new_queries += 1
            time.sleep(0.2)  # Respectful delay for the API
        except ValueError:
            flood_zones.append("Invalid coordinates")
            total_queries += 0
    else:
        flood_zones.append("Missing coordinates")
        total_queries += 0

# Save results
df['Flood Zone'] = flood_zones
df.to_csv(output_file, index=False)

print(f"Flood zone info saved to '{output_file}'.")
print(f"Total properties processed: {len(df)}")
print(f"Queries saved using cache: {len(df) - new_queries}")
print(f"New queries made: {new_queries}")