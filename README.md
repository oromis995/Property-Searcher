# RedFin Property Data Scraper

This Python project consists of three scripts that extract property data from RedFin, calculate drive times, and check flood zones for the properties.

## Scripts

### 1. `1_get_properties.py`
Queries RedFin and retrieves all properties from a given URL where filters have already been applied on the RedFin website.

### 2. `2_get_drive_time.py`
Calculates drive times from each property to a specified address.

### 3. `3_get_flood_zone.py`
Retrieves flood zone information for each property.

## Requirements

- Python 3.x
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
