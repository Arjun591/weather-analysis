from pymongo import MongoClient
import os
import pandas as pd

from dotenv import load_dotenv

load_dotenv()

def get_connection():
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    db = client['weather_analysis']
    return db
def insert_data(df):
    db = get_connection()
    collection = db['weather_data']

    if collection.count_documents({}) > 0:
        print(" Data already exists in Atlas, skipping insert")
        return
# TEMP: comment out the return above to force reinsert

    print(" Inserting data into MongoDB Atlas...")
    records = df.to_dict('records')

    # Insert in batches of 1000 to avoid timeout
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        collection.insert_many(batch)
        print(f"   Inserted {min(i + batch_size, len(records))}/{len(records)} records")

    print(" All data inserted into MongoDB Atlas!")

def fetch_data():
    db = get_connection()
    collection = db['weather_data']
    print(" Fetching data from MongoDB Atlas...")
    df = pd.DataFrame(list(collection.find()))
    if '_id' in df.columns:
        df.drop('_id', axis=1, inplace=True)

    # Clean data same as load_data
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    df['country'] = df['country'].str.strip()
    df['location_name'] = df['location_name'].str.strip()
    df['condition_text'] = df['condition_text'].str.strip()

    print(f" Fetched {len(df)} records from MongoDB Atlas")
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