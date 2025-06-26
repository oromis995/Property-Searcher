#!/bin/bash

# Exit if any command fails
set -e

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Upgrade pip and install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run Python scripts in sequence
echo "Running 1_get_properties.py..."
python 1_get_properties.py

echo "Running 2_get_drive_time.py..."
python 2_get_drive_time.py

echo "Running 3_get_flood_zone.py..."
python 3_get_flood_zone.py

echo "Running 4_filter_properties.py..."
python 4_filter_properties.py

echo "Running 5_ui.py..."
python 5_ui.py

echo "All scripts executed successfully."
