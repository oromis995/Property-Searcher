import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

base_url = "https://www.redfin.com/county/1255/LA/Jefferson-Parish/filter/property-type=house+townhouse+multifamily,max-price=220k,min-beds=2,min-baths=1.5,min-sqft=1.2k-sqft,hoa=0"

properties = []
page_num = 1

while True:
    print(f"Processing page {page_num}...")
    
    url = f"{base_url}/page-{page_num}" if page_num > 1 else base_url

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Stopping at page {page_num}")
        break

    soup = BeautifulSoup(response.text, 'html.parser')
    property_cards = soup.find_all('div', class_='MapHomeCardReact')
    
    if not property_cards:
        print("No more properties found.")
        break

    for card in property_cards:
        try:
            address = card.find('div', class_='bp-Homecard__Address').get_text(strip=True)
            price = card.find('span', class_='bp-Homecard__Price--value').get_text(strip=True)
            
            stats = card.find('div', class_='bp-Homecard__Stats')
            beds = stats.find('span', class_='bp-Homecard__Stats--beds').get_text(strip=True)
            baths = stats.find('span', class_='bp-Homecard__Stats--baths').get_text(strip=True)
            sqft = stats.find('span', class_='bp-Homecard__Stats--sqft').get_text(strip=True)
            
            lot_size = "N/A"
            key_facts = card.find('div', class_='KeyFactsExtension')
            if key_facts:
                lot_size = key_facts.find('span', class_='KeyFacts-item').get_text(strip=True)
            
            property_url = urljoin(url, card.find('a', class_='bp-Homecard')['href'])
            
            properties.append({
                'Address': address,
                'Price': price,
                'Beds': beds,
                'Baths': baths,
                'Square Feet': sqft,
                'Lot Size': lot_size,
                'URL': property_url,
                'City': 'New Orleans'  # Default to New Orleans
            })
        except Exception as e:
            print(f"Skipping a property: {e}")
            continue

    page_num += 1
    time.sleep(1)

csv_filename = 'redfin_properties.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Address', 'Price', 'Beds', 'Baths', 'Square Feet', 'Lot Size', 'URL', 'City']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(properties)

print(f"Saved {len(properties)} properties to {csv_filename}")