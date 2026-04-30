from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pandas as pd
import pickle

load_dotenv()

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache.pkl')

def get_connection():
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    db = client['weather_analysis']
    return db

def insert_data(df):
    db = get_connection()
    collection = db['weather_data']
    if collection.count_documents({}) > 0:
        print("Data already exists in Atlas, skipping insert")
        return
    print("📦 Inserting data into MongoDB Atlas...")
    records = df.to_dict('records')
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        collection.insert_many(batch)
        print(f" Inserted {min(i + batch_size, len(records))}/{len(records)} records")
    print("All data inserted into MongoDB Atlas!")
    # Clear cache after new insert
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)

def fetch_data():
    # Check local cache first
    if os.path.exists(CACHE_FILE):
        print("Loading from local cache...")
        with open(CACHE_FILE, 'rb') as f:
            df = pickle.load(f)
        print(f"Loaded {len(df)} records from cache")
        return df

    # Fetch from Atlas
    db = get_connection()
    collection = db['weather_data']
    print("Fetching data from MongoDB Atlas...")
    df = pd.DataFrame(list(collection.find()))
    if '_id' in df.columns:
        df.drop('_id', axis=1, inplace=True)

    # Clean data
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    df['country'] = df['country'].str.strip()
    df['location_name'] = df['location_name'].str.strip()
    df['condition_text'] = df['condition_text'].str.strip()

    print(f"Fetched {len(df)} records from Atlas")

    print("Saving to local cache...")
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(df, f)
    print("Cache saved!")

    return df

def get_summary_stats():
    db = get_connection()
    collection = db['weather_data']
    stats = {
        'total_records': collection.count_documents({}),
        'total_countries': len(collection.distinct('country')),
        'total_cities': len(collection.distinct('location_name')),
    }
    return stats

def get_aggregated_data(group_by, metric, operation='avg'):
    """Fetch aggregated data directly from Atlas instead of all rows"""
    db = get_connection()
    collection = db['weather_data']

    op = f"${operation}"
    pipeline = [
        {"$group": {
            "_id": f"${group_by}",
            "value": {op: f"${metric}"}
        }},
        {"$sort": {"value": -1}},
        {"$limit": 15}
    ]
    result = list(collection.aggregate(pipeline))
    df = pd.DataFrame(result)
    if not df.empty:
        df.columns = [group_by, metric]
    return df