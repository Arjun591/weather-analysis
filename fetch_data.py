import warnings
warnings.filterwarnings("ignore")

from src.fetch_historical import fetch_and_store_all

print("🌍 Starting historical data fetch...")
print("This will take 20-30 minutes...\n")
fetch_and_store_all(start_year=2015)