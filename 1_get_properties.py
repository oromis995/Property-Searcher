import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import time

# Set headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Base URL of the Redfin search page
base_url = "https://www.redfin.com/county/1255/LA/Jefferson-Parish/filter/property-type=house+townhouse+multifamily,max-price=220k,min-beds=2,min-baths=1.5,min-sqft=1.2k-sqft,hoa=0"

# Prepare data list
properties = []
page_num = 1

while True:
    print(f"Processing page {page_num}...")
    
    # For pages after the first, append the page number
    if page_num > 1:
        url = f"{base_url}/page-{page_num}"
    else:
        url = base_url

    # Send a GET request to the URL
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Reached end of pages or encountered error at page {page_num}")
        break

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all property cards
    property_cards = soup.find_all('div', class_='MapHomeCardReact')
    
    # If no property cards found, we've reached the end
    if not property_cards:
        print("No more properties found.")
        break

    for card in property_cards:
        try:
            # Extract image source
            img_src = card.find('img', class_='bp-Homecard__Photo--image')['src']
            if not img_src.startswith('http'):
                img_src = f"https:{img_src}"
            
            # Extract property details
            address = card.find('div', class_='bp-Homecard__Address').get_text(strip=True)
            price = card.find('span', class_='bp-Homecard__Price--value').get_text(strip=True)
            
            # Extract stats (beds, baths, sqft)
            stats = card.find('div', class_='bp-Homecard__Stats')
            beds = stats.find('span', class_='bp-Homecard__Stats--beds').get_text(strip=True)
            baths = stats.find('span', class_='bp-Homecard__Stats--baths').get_text(strip=True)
            sqft = stats.find('span', class_='bp-Homecard__Stats--sqft').get_text(strip=True)

            # Extract additional details if available
            key_facts = card.find('div', class_='KeyFactsExtension')
            if key_facts:
                lot_size = key_facts.find('span', class_='KeyFacts-item').get_text(strip=True)
            else:
                lot_size = "N/A"
            
            # Get the property URL
            property_url = card.find('a', class_='bp-Homecard')['href']
            full_property_url = urljoin(url, property_url)
            
            # Add to properties list
            properties.append({
                'Image': f'=IMAGE("{img_src}")',  # Excel formula to embed image
                'Address': address,
                'Price': price,
                'Beds': beds,
                'Baths': baths,
                'Square Feet': sqft,
                'Lot Size': lot_size,
                'URL': full_property_url
            })
        except Exception as e:
            print(f"Error processing a property card: {e}")
            continue

    # Check if there's a next page button
    next_page_button = soup.find('span', class_='ButtonLabel', string=str(page_num + 1))
    if not next_page_button:
        print("No more pages found.")
        break

    # Increment page number and add a small delay
    page_num += 1
    time.sleep(1)  # Be polite with delays between requests

# Export to CSV
csv_filename = 'redfin_properties.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Image', 'Address', 'Price', 'Beds', 'Baths', 'Square Feet', 'Lot Size', 'URL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for prop in properties:
        writer.writerow(prop)

print(f"Successfully exported {len(properties)} properties from {page_num} pages to {csv_filename}")