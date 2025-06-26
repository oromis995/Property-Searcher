import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import time
import re
import os
from urllib.request import urlretrieve, URLError

# Configuration
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
base_url = "https://www.redfin.com/county/1255/LA/Jefferson-Parish/filter/property-type=house+townhouse+multifamily,max-price=220k,min-beds=2,min-baths=1.5,min-sqft=1.2k-sqft,hoa=0"
output_csv = '1_properties.csv'
photo_base_dir = 'Photos'

# Create directories if they don't exist
os.makedirs(photo_base_dir, exist_ok=True)

def clean_filename(text):
    return re.sub(r'[<>:"/\\|?*]', '', text.strip())

def download_images_from_base(preview_url, photo_dir):
    os.makedirs(photo_dir, exist_ok=True)

    # Match pattern from preview image URL
    match = re.search(r'photo/(\d+)/islphoto/(\d+)/[^.]*\.(\d+)_(\d)\.jpg', preview_url)
    if not match:
        print(f"Could not parse image preview URL: {preview_url}")
        return

    region, folder, base_id, top_id = match.groups()
    
    for i in range(30):  # Try up to 30 images
        if i == 0:
            img_url = f"https://ssl.cdn-redfin.com/photo/{region}/bigphoto/{folder}/{base_id}_{top_id}.jpg"
        else:
            img_url = f"https://ssl.cdn-redfin.com/photo/{region}/bigphoto/{folder}/{base_id}_{i}_{top_id}.jpg"

        img_path = os.path.join(photo_dir, f"{i:04d}.jpg")
        if os.path.exists(img_path):
            continue

        try:
            response = requests.get(img_url, stream=True, timeout=5)
            if response.status_code == 200:
                with open(img_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Downloaded: {img_url}")
            else:
                if i == 0:
                    print(f"First image not found for: {base_id}")
                break  # Stop if image doesn't exist (likely end of photo set)
        except URLError as e:
            print(f"Failed to download {img_url}: {e}")
            break

def extract_property_data(card, url):
    try:
        address = card.find('div', class_='bp-Homecard__Address').get_text(strip=True)
        address_parts = [part.strip() for part in address.split(',')]

        street = address_parts[0] if address_parts else "N/A"
        city = address_parts[1] if len(address_parts) > 1 else "N/A"
        state_zip = address_parts[2] if len(address_parts) > 2 else "N/A N/A"
        state, zip_code = (state_zip.split() + ["N/A", "N/A"])[:2]

        price = card.find('span', class_='bp-Homecard__Price--value').get_text(strip=True).replace('$', '').replace(',', '')
        stats = card.find('div', class_='bp-Homecard__Stats')

        def clean_stat(text, pattern):
            return re.sub(pattern, '', text, flags=re.IGNORECASE).replace(',', '').strip()

        beds = clean_stat(stats.find('span', class_='bp-Homecard__Stats--beds').get_text(strip=True), r'\s*beds?')
        baths = clean_stat(stats.find('span', class_='bp-Homecard__Stats--baths').get_text(strip=True), r'\s*baths?')
        sqft = clean_stat(stats.find('span', class_='bp-Homecard__Stats--sqft').get_text(strip=True), r'\s*sq\s*ft')

        property_url = urljoin(url, card.find('a', class_='bp-Homecard')['href'])

        # Extract preview image to derive full set
        img_tag = card.find('img', class_='bp-Homecard__Photo--image')
        preview_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else None

        photo_dir = os.path.join(photo_base_dir, f"{zip_code}_{clean_filename(street)}")
        if preview_url:
            if not preview_url.startswith("http"):
                preview_url = f"https:{preview_url}"
            download_images_from_base(preview_url, photo_dir)

        return {
            'Street': street,
            'City': city,
            'State': state,
            'ZIP Code': zip_code,
            'Price': price,
            'Beds': beds,
            'Baths': baths,
            'Square Feet': sqft,
            'URL': property_url
        }
    except Exception as e:
        print(f"Error processing property: {e}")
        return None

def scrape_redfin():
    properties = []
    page_num = 1

    while True:
        print(f"Processing page {page_num}...")
        url = f"{base_url}/page-{page_num}" if page_num > 1 else base_url

        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Stopped at page {page_num} (status code: {response.status_code})")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            property_cards = soup.find_all('div', class_='MapHomeCardReact')

            if not property_cards:
                print("No more properties found.")
                break

            for card in property_cards:
                prop_data = extract_property_data(card, url)
                if prop_data:
                    properties.append(prop_data)

            if not soup.find('span', class_='ButtonLabel', string=str(page_num + 1)):
                break

            page_num += 1
            time.sleep(1)

        except Exception as e:
            print(f"Error processing page {page_num}: {e}")
            break

    if properties:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=properties[0].keys())
            writer.writeheader()
            writer.writerows(properties)
        print(f"Saved {len(properties)} properties to {output_csv}")

if __name__ == '__main__':
    scrape_redfin()
