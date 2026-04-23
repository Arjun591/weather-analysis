import pandas as pd
import numpy as np
import os

def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'globalweatherrepository.csv')

    df = pd.read_csv(file_path)

    # Convert date column
    df['last_updated'] = pd.to_datetime(df['last_updated'])

    # Clean text columns
    df['country'] = df['country'].str.strip()
    df['location_name'] = df['location_name'].str.strip()
    df['condition_text'] = df['condition_text'].str.strip()

    # Clean bad air quality values
    aq_cols = ['air_quality_Carbon_Monoxide', 'air_quality_Ozone',
               'air_quality_Nitrogen_dioxide', 'air_quality_Sulphur_dioxide',
               'air_quality_PM2.5', 'air_quality_PM10']
    for col in aq_cols:
        df[col] = df[col].replace(-9999, np.nan)

    print(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df

def get_countries(df):
    return sorted(df['country'].unique().tolist())

def get_cities(df, country=None):
    if country:
        return sorted(df[df['country'] == country]['location_name'].unique().tolist())
    return sorted(df['location_name'].unique().tolist())

def filter_by_country(df, country):
    return df[df['country'] == country]

def filter_by_city(df, city):
    return df[df['location_name'] == city]

def filter_by_date(df, start_date, end_date):
    return df[(df['last_updated'] >= start_date) & 
              (df['last_updated'] <= end_date)]