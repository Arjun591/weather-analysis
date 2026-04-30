import requests
import pandas as pd
from datetime import datetime
import time
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    return client['weather_analysis']

def get_all_cities():
    """
    Automatically get cities from:
    1. Our existing Atlas dataset
    2. REST Countries + GeoDB free APIs
    """
    cities = []
    existing_names = set()

    # Step 1 — existing cities from Atlas
    print("📦 Loading cities from Atlas...")
    try:
        db = get_connection()
        records = list(db['weather_data'].aggregate([
            {"$group": {
                "_id": "$location_name",
                "country": {"$first": "$country"},
                "latitude": {"$first": "$latitude"},
                "longitude": {"$first": "$longitude"}
            }}
        ]))
        for c in records:
            if c['_id'] and c.get('latitude') and c.get('longitude'):
                cities.append({
                    "city": c['_id'],
                    "country": c['country'],
                    "lat": c['latitude'],
                    "lon": c['longitude']
                })
                existing_names.add(c['_id'].lower())
        print(f"✅ {len(cities)} cities from existing dataset")
    except Exception as e:
        print(f"⚠️ Could not load from Atlas: {e}")

    # Step 2 — get more cities from GeoDB API (free, no key needed)
    print("\n🌍 Fetching more cities from GeoDB API...")
    try:
        # GeoDB cities API — returns top cities by population worldwide
        url = "http://geodb-free-service.wirefreethought.com/v1/geo/places"
        params = {
            "limit": 100,
            "offset": 0,
            "minPopulation": 500000,  # cities with 500k+ population
            "sort": "-population",
            "types": "CITY"
        }

        total_fetched = 0
        max_cities = 500

        while total_fetched < max_cities:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code != 200:
                break

            data = response.json()
            results = data.get('data', [])
            if not results:
                break

            for city_data in results:
                city_name = city_data.get('name', '')
                country = city_data.get('country', '')
                lat = city_data.get('latitude')
                lon = city_data.get('longitude')

                if city_name and lat and lon and city_name.lower() not in existing_names:
                    cities.append({
                        "city": city_name,
                        "country": country,
                        "lat": lat,
                        "lon": lon
                    })
                    existing_names.add(city_name.lower())
                    total_fetched += 1

            # Next page
            total_count = data.get('metadata', {}).get('totalCount', 0)
            params['offset'] += params['limit']
            if params['offset'] >= min(total_count, max_cities):
                break

            time.sleep(1)  # GeoDB rate limit

        print(f"✅ Added {total_fetched} more cities from GeoDB")
    except Exception as e:
        print(f"⚠️ GeoDB failed: {e}")
        # Fallback to Open-Meteo geocoding popular countries
        print("🔄 Falling back to country capitals...")
        cities = get_country_capitals(cities, existing_names)

    print(f"\n✅ Total cities: {len(cities)}")
    return cities

def get_country_capitals(cities, existing_names):
    """Fallback — get capitals of all countries using REST Countries API"""
    try:
        response = requests.get(
            "https://restcountries.com/v3.1/all?fields=name,capital,capitalInfo",
            timeout=15
        )
        if response.status_code == 200:
            countries = response.json()
            print(f"🌍 Found {len(countries)} countries")

            for country in countries:
                capitals = country.get('capital', [])
                capital_info = country.get('capitalInfo', {})
                latlng = capital_info.get('latlng', [])
                country_name = country.get('name', {}).get('common', '')

                if capitals and latlng and len(latlng) == 2:
                    capital = capitals[0]
                    if capital.lower() not in existing_names:
                        cities.append({
                            "city": capital,
                            "country": country_name,
                            "lat": latlng[0],
                            "lon": latlng[1]
                        })
                        existing_names.add(capital.lower())

            print(f"✅ Added capitals, total: {len(cities)}")
    except Exception as e:
        print(f"⚠️ REST Countries failed: {e}")
    return cities

def fetch_city_historical(city_info, start_year=2015):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": city_info["lat"],
        "longitude": city_info["lon"],
        "start_date": f"{start_year}-01-01",
        "end_date": datetime.now().strftime("%Y-%m-%d"),
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "windspeed_10m_max",
            "relative_humidity_2m_max",
            "relative_humidity_2m_min",
            "pressure_msl_mean",
            "uv_index_max"
        ],
        "timezone": "auto"
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)

            # Rate limited — wait 60 seconds and retry
            if response.status_code == 429:
                print(f"  ⏳ Rate limited! Waiting 60 seconds...")
                time.sleep(90)
                continue

            if response.status_code != 200:
                return None

            data = response.json()

            if 'error' in data:
                print(f"  API Error: {data.get('reason', '')}")
                return None

            daily = data.get('daily', {})
            if not daily or 'time' not in daily:
                return None

            df = pd.DataFrame({
                'date':          daily['time'],
                'city':          city_info['city'],
                'country':       city_info['country'],
                'latitude':      city_info['lat'],
                'longitude':     city_info['lon'],
                'temp_max':      daily.get('temperature_2m_max', []),
                'temp_min':      daily.get('temperature_2m_min', []),
                'temp_mean':     daily.get('temperature_2m_mean', []),
                'precipitation': daily.get('precipitation_sum', []),
                'wind_max':      daily.get('windspeed_10m_max', []),
                'humidity_max':  daily.get('relative_humidity_2m_max', []),
                'humidity_min':  daily.get('relative_humidity_2m_min', []),
                'pressure':      daily.get('pressure_msl_mean', []),
                'uv_index':      daily.get('uv_index_max', []),
            })

            df['humidity_mean'] = (df['humidity_max'] + df['humidity_min']) / 2
            df['date'] = pd.to_datetime(df['date'])
            return df

        except Exception as e:
            print(f"  ❌ Exception: {e}")
            time.sleep(5)

    return None
def get_coordinates(city_name):
    """Get lat/lon for a city using Open-Meteo geocoding API"""
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            results = response.json().get('results', [])
            if results:
                return {
                    "lat": results[0]['latitude'],
                    "lon": results[0]['longitude'],
                    "country": results[0].get('country', 'Unknown')
                }
    except Exception:
        pass
    return None
def fetch_and_store_all(start_year=2015):
    db = get_connection()
    collection = db['historical_data']

    # Get city names from Atlas
    print("📦 Loading cities from Atlas...")
    records = list(db['weather_data'].aggregate([
        {"$group": {
            "_id": "$location_name",
            "country": {"$first": "$country"},
        }}
    ]))
    print(f"✅ {len(records)} cities from existing dataset")

    # Skip already fetched
    already_fetched = set(collection.distinct('city'))
    cities_to_fetch = [r for r in records if r['_id'] not in already_fetched]
    print(f"⏭️  Already fetched: {len(already_fetched)}")
    print(f"📥 To fetch: {len(cities_to_fetch)}\n")

    success = 0
    failed = []

    for idx, record in enumerate(cities_to_fetch):
        city_name = record['_id']
        country = record['country']
        print(f"[{idx+1}/{len(cities_to_fetch)}] {city_name}, {country}...")

        # Get fresh coordinates
        coords = get_coordinates(f"{city_name} {country}")
        if not coords:
            coords = get_coordinates(city_name)

        if not coords:
            print(f"  ⚠️ Coordinates not found")
            failed.append(record)
            time.sleep(0.5)
            continue

        city_info = {
            "city": city_name,
            "country": country,
            "lat": coords['lat'],
            "lon": coords['lon']
        }

        df = fetch_city_historical(city_info, start_year)

        if df is not None and not df.empty:
            records_to_insert = df.to_dict('records')
            collection.insert_many(records_to_insert)
            print(f"  ✅ {len(records_to_insert)} records")
            success += 1
        else:
            print(f"  ⚠️ No data — will retry later")
            failed.append(record)

        time.sleep(15)  # ← increased delay to avoid rate limiting

    # Retry failed cities once
    if failed:
        print(f"\n🔄 Retrying {len(failed)} failed cities...")
        time.sleep(5)  # wait 5 seconds before retrying

        for record in failed:
            city_name = record['_id']
            country = record['country']
            print(f"  Retrying {city_name}...")

            coords = get_coordinates(f"{city_name} {country}")
            if not coords:
                coords = get_coordinates(city_name)
            if not coords:
                continue

            city_info = {
                "city": city_name,
                "country": country,
                "lat": coords['lat'],
                "lon": coords['lon']
            }

            df = fetch_city_historical(city_info, start_year)
            if df is not None and not df.empty:
                records_to_insert = df.to_dict('records')
                collection.insert_many(records_to_insert)
                print(f"  ✅ {len(records_to_insert)} records")
                success += 1

            time.sleep(15)  # longer delay for retries

    print(f"\n🎉 Done!")
    print(f"✅ Success: {success} cities")
    print(f"📊 Total records in Atlas: {collection.count_documents({})}")

    print(f"\n🎉 Done! Total: {collection.count_documents({})} records")