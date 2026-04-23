import pandas as pd
import numpy as np

def temperature_summary(df):
    return {
        'mean': round(df['temperature_celsius'].mean(), 2),
        'max': round(df['temperature_celsius'].max(), 2),
        'min': round(df['temperature_celsius'].min(), 2),
        'std': round(df['temperature_celsius'].std(), 2)
    }

def temperature_by_country(df, top_n=10):
    return (df.groupby('country')['temperature_celsius']
              .mean()
              .sort_values(ascending=False)
              .head(top_n)
              .reset_index()
              .rename(columns={'temperature_celsius': 'avg_temperature'}))

def temperature_trends(df):
    df = df.copy()
    df['month'] = df['last_updated'].dt.to_period('M')
    trends = df.groupby('month')['temperature_celsius'].agg(['mean', 'min', 'max']).reset_index()
    trends['month'] = trends['month'].astype(str)
    return trends

def humidity_by_country(df, top_n=10):
    return (df.groupby('country')['humidity']
              .mean()
              .sort_values(ascending=False)
              .head(top_n)
              .reset_index()
              .rename(columns={'humidity': 'avg_humidity'}))

def precipitation_trends(df):
    df = df.copy()
    df['month'] = df['last_updated'].dt.to_period('M')
    return (df.groupby('month')['precip_mm']
              .sum()
              .reset_index()
              .assign(month=lambda x: x['month'].astype(str)))

def wind_by_country(df, top_n=10):
    return (df.groupby('country')['wind_kph']
              .mean()
              .sort_values(ascending=False)
              .head(top_n)
              .reset_index()
              .rename(columns={'wind_kph': 'avg_wind_kph'}))

def air_quality_by_country(df, top_n=10):
    return (df.groupby('country')['air_quality_PM2.5']
              .mean()
              .sort_values(ascending=False)
              .head(top_n)
              .reset_index()
              .rename(columns={'air_quality_PM2.5': 'avg_PM2.5'}))

def condition_distribution(df):
    data = df['condition_text'].value_counts().head(10).reset_index()
    data.columns = ['condition', 'count']
    return data

def compare_cities(df, cities):
    return (df[df['location_name'].isin(cities)]
              .groupby('location_name')[['temperature_celsius', 'humidity', 'wind_kph', 'precip_mm']]
              .mean()
              .reset_index())

def monthly_avg(df, column):
    df = df.copy()
    df['month'] = df['last_updated'].dt.to_period('M')
    return (df.groupby('month')[column]
              .mean()
              .reset_index()
              .assign(month=lambda x: x['month'].astype(str)))