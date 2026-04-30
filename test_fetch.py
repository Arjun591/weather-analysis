import warnings
warnings.filterwarnings("ignore")
from src.fetch_historical import get_coordinates, fetch_city_historical

# Test with London
city_name = "London"
print(f"Getting coordinates for {city_name}...")
coords = get_coordinates(city_name)
print(f"Coordinates: {coords}")

if coords:
    city_info = {
        "city": city_name,
        "country": "United Kingdom",
        "lat": coords['lat'],
        "lon": coords['lon']
    }
    print(f"\nFetching historical data...")
    df = fetch_city_historical(city_info, start_year=2020)
    if df is not None:
        print(f"Success! {len(df)} records")
        print(df.head())
    else:
        print("Failed!")