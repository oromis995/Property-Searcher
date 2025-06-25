import pandas as pd
import requests
import time

# Load CSV
df = pd.read_csv('properties_with_drive_times.csv')

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
for coord in df['Coordinates']:
    if isinstance(coord, str) and "," in coord:
        try:
            lat, lon = map(float, coord.strip().split(","))
            zone = get_flood_zone(lat, lon)
        except ValueError:
            zone = "Invalid coordinates"
    else:
        zone = "Missing coordinates"
    flood_zones.append(zone)
    time.sleep(0.2)  # Respectful delay for the API

# Save results
df['Flood Zone'] = flood_zones
df.to_csv('properties_with_flood_zones.csv', index=False)

print("Flood zone info saved to 'properties_with_flood_zones.csv'.")
