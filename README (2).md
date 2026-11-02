# Pune Care Map

An interactive map of **5,703 health places in Pune** (hospitals, pharmacies, dental clinics, labs, specialists and clinics). Filter by type, search by name, and **click anywhere to find the 3 nearest places by road**, with real driving distance and time from AWS.

Built for the AWS Weekend Challenge: **Map it**.

- **Live map:** [ADD LIVE LINK HERE]
- **Demo video (under 3 min):** [ADD VIDEO LINK HERE]

## What you can do on the map
- See every health place as a dot, coloured by type (red = hospital, green = pharmacy, and so on).
- Zoom out and dots group into numbered clusters. Click a cluster to zoom in.
- Tick or untick types, or type a name in the search box (press Enter to zoom to the results).
- Pick a type in "Find the nearest", then click anywhere on the map. You get the 3 nearest by road, drawn as routes, with distance and time.

## The dataset
- **Source:** [Overture Maps Foundation](https://overturemaps.org) Places, release `2026-10-21.0`.
- **Where it comes from:** the [Registry of Open Data on AWS](https://registry.opendata.aws/overture/). It is read directly from a public S3 bucket (`s3://overturemaps-us-west-2/release/2026-10-21.0/theme=places/`), so no AWS account is needed to get the raw data.
- **What I took:** places inside a box around Pune (longitude 73.70 to 74.05, latitude 18.40 to 18.65) in health-related categories: 7,149 rows.
- **How I cleaned it (`scripts/clean_data.py`):**
  - removed places with no name
  - removed low-confidence places (confidence below 0.5)
  - removed duplicates and anything outside the Pune box
  - grouped categories into 6 simple types
  - kept the English part of names like `Marathi name - English name`
  - result: **5,703 places** in `pune_health_clean.csv` with 4 columns: `name, type, lon, lat`
- Data attribution: Overture Maps Foundation. See [docs.overturemaps.org](https://docs.overturemaps.org) for attribution and license terms.

## AWS services used
| Service | What it does here |
|---|---|
| **Amazon Location Service (Maps)** | Draws the base map in the browser (Standard style, via an API key). |
| **Amazon Location Service (Routes, CalculateRoutes)** | Gives the real driving route, distance and time for the nearest-places feature. |
| **Registry of Open Data on AWS / Amazon S3** | Source of the raw Overture data (public bucket), and storage for the cleaned CSV. |

The API key is limited to Maps and Routes actions only, and to this website's address.

## How it works
```
Overture Places (public S3, Parquet)
        |  DuckDB query (scripts/get_data.py)
        v
   pune_health.csv  --clean-->  pune_health_clean.csv
        |
        v
   index.html  (MapLibre GL JS + Papa Parse)
        |  base map tiles + CalculateRoutes
        v
   Amazon Location Service
```
1. The page loads the CSV and turns each row into a GeoJSON point.
2. MapLibre draws the points as a clustered source with colour-coded layers.
3. For "nearest", the page picks the closest candidates in a straight line (in the browser), then asks the Amazon Location **Routes API** for the real driving routes to those 3 only.

## Reuse this pattern
You can swap in any dataset that has coordinates:
1. Change the bounding box and categories in `scripts/get_data.py` (or use your own CSV with `name, type, lon, lat`).
2. Create an Amazon Location **API key** (Maps and Routes actions), and put it in `config.js`.
3. Edit `TYPE_COLORS` in `index.html` to match your categories. The dots, filters and dropdown all update from that one list.

## Run it locally
```bash
python -m http.server 8000
# open http://localhost:8000/index.html
```
`config.js` needs your own Amazon Location API key:
```js
const API_KEY = "your key";
const REGION = "us-east-1";
```
To rebuild the data:
```bash
pip install duckdb
python scripts/get_data.py
python scripts/clean_data.py
```
(Overture keeps only the last two monthly releases online, so update `RELEASE` in `get_data.py` to a current one.)

## Notes and limits
- Overture data can have mistakes (wrong categories, closed places, odd names). Always confirm before travelling to a hospital in an emergency.
- Route times are estimates from the Routes API.
- Not medical advice.
