# 🏠 Property Searcher

**Property Searcher** is a Python-based tool that automates the discovery, evaluation, and visualization of real estate listings. It scrapes data from Redfin, calculates drive times to a specified address, checks flood zone status via FEMA, filters properties based on customizable criteria, and provides a user-friendly GUI for review and browsing of saved listings with image previews.

---

## 📁 Project Structure

```
📂 Property Searcher
├── 📄 1_get_properties.py           # Scrapes Redfin listings and saves basic info + images
├── 📄 2_get_drive_time.py           # Geocodes addresses and computes drive time using OSRM
├── 📄 3_get_flood_zone.py           # Retrieves FEMA flood zone data
├── 📄 4_filter_properties.py        # Filters properties by drive time and flood risk
├── 📄 5_ui.py                       # Tkinter-based GUI for browsing and viewing saved listings
├── 📄 requirements.txt              # Python dependencies
├── 📄 run.ps1                       # PowerShell script to run pipeline
└── 📄 run.sh                        # Shell script to run pipeline
```

---

## 🚀 Features

- 🔍 **Redfin Scraping**: Collects address, price, beds, baths, square footage, and images.
- 🗺️ **Drive Time Analysis**: Calculates distance and time from each property to a target destination.
- 🌊 **Flood Zone Checker**: Uses FEMA's NFHL to determine flood risk.
- ✅ **Property Filtering**: Filters out flood-prone areas and long commutes.
- 🖼️ **Interactive Viewer**: GUI with property data grid, image gallery, and details panel.

---

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/oromis995/Property-Searcher.git
   cd Property-Searcher
   ```

2. **Install Python (if not already installed)**  
   Download and install Python 3.7 or higher from the official site:  
   👉 https://www.python.org/downloads/

   Be sure to check the box **"Add Python to PATH"** during installation.

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure the following are accessible:**
   - Internet access (for API requests to Redfin, OSRM, FEMA)
   - Python 3.7+
   - OSRM routing (via default public instance)

---

## 🧪 Usage

### 🔗 Full Pipeline (Scrape → Analyze → Filter → GUI)

```bash
bash run.sh
# OR on Windows:
./run.ps1
```

> 💡 **Windows Users**:  
> To open PowerShell:
> - Press `Win + X` and choose **Windows PowerShell**, or  
> - Press `Win + R`, type `powershell`, and hit Enter.

### 🔍 Step-by-step

1. **Scrape Redfin listings**
   ```bash
   python 1_get_properties.py
   ```

2. **Add drive time data**
   ```bash
   python 2_get_drive_time.py
   ```

3. **Check FEMA flood zones**
   ```bash
   python 3_get_flood_zone.py
   ```

4. **Filter by drive time and flood zone**
   ```bash
   python 4_filter_properties.py
   ```

5. **Launch the GUI viewer**
   ```bash
   python 5_ui.py
   ```

---

## ⚙️ Customization

### 🏁 Change Destination Address

To change the address used for drive time calculations:

- Open `2_get_drive_time.py`
- Find this line near the top:

  ```python
  destination = "781 Lasalle St, New Orleans, LA 70112"
  ```

- Replace it with your desired address:

  ```python
  destination = "123 Main St, YourCity, ST 12345"
  ```

### ⏱️ Adjust Drive Time Limit

To change the maximum allowed drive time (default is 25 minutes):

- Open `4_filter_properties.py`
- Locate the line:

  ```python
  if drive_time > 25:
  ```

- Change `25` to your preferred limit in minutes:

  ```python
  if drive_time > 20:
  ```

---

## 🖼️ GUI Preview

- Interactive table of properties with sorting
- On-click image gallery for each property
- Details panel with key metadata

---

## 📊 Filtering Logic

- ✅ Drive Time ≤ 25 minutes (configurable)
- 🚫 Flood Zone starts with "AE" → Excluded
- ✅ Non-AE flood zones or "Not in mapped flood zone" → Included

---

## 📷 Image Download

- Downloads up to 30 photos per property
- Saved in `Photos/ZIPCODE_STREETNAME/`
- Images linked from Redfin previews and constructed from CDN patterns

---

## 🌐 APIs & Data Sources

- [Redfin](https://www.redfin.com/) – Property listings
- [ArcGIS Geocoding API](https://developers.arcgis.com/rest/geocode/api-reference/overview-world-geocoding-service.htm)
- [OSRM Routing](http://project-osrm.org/)
- [FEMA NFHL](https://hazards.fema.gov/)

---

## 🙌 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a new feature branch
3. Submit a pull request with detailed explanation

---

## ⚠️ Disclaimer

This tool is provided for educational and research purposes only. Scraping websites or using APIs should be done in compliance with their terms of service. Always respect data usage policies and rate limits.

---

## 📃 License

MIT License. See [LICENSE](LICENSE) for details.

---
