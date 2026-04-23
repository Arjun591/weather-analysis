import matplotlib.pyplot as plt
import matplotlib.figure as fig
from src.analysis import (temperature_by_country, temperature_trends,
                           humidity_by_country, precipitation_trends,
                           wind_by_country, air_quality_by_country,
                           condition_distribution)

def plot_temperature_by_country(df, top_n=10):
    data = temperature_by_country(df, top_n)
    figure, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(data['country'], data['avg_temperature'], color='tomato')
    ax.set_xlabel('Average Temperature (°C)')
    ax.set_title(f'Top {top_n} Hottest Countries')
    ax.invert_yaxis()
    for bar, val in zip(bars, data['avg_temperature']):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}°C', va='center', fontsize=9)
    plt.tight_layout()
    return figure

def plot_temperature_trends(df):
    data = temperature_trends(df)
    figure, ax = plt.subplots(figsize=(12, 5))
    ax.plot(data['month'], data['mean'], marker='o', label='Avg Temp', color='orange')
    ax.plot(data['month'], data['max'], linestyle='--', label='Max Temp', color='red')
    ax.plot(data['month'], data['min'], linestyle='--', label='Min Temp', color='blue')
    ax.set_xlabel('Month')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Global Temperature Trends Over Time')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return figure

def plot_humidity(df, top_n=10):
    data = humidity_by_country(df, top_n)
    figure, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(data['country'], data['avg_humidity'], color='steelblue')
    ax.set_xlabel('Average Humidity (%)')
    ax.set_title(f'Top {top_n} Most Humid Countries')
    ax.invert_yaxis()
    for bar, val in zip(bars, data['avg_humidity']):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}%', va='center', fontsize=9)
    plt.tight_layout()
    return figure

def plot_precipitation(df):
    data = precipitation_trends(df)
    figure, ax = plt.subplots(figsize=(12, 5))
    ax.bar(data['month'], data['precip_mm'], color='royalblue')
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Precipitation (mm)')
    ax.set_title('Global Total Precipitation by Month')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return figure

def plot_wind(df, top_n=10):
    data = wind_by_country(df, top_n)
    figure, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(data['country'], data['avg_wind_kph'], color='mediumseagreen')
    ax.set_xlabel('Average Wind Speed (kph)')
    ax.set_title(f'Top {top_n} Windiest Countries')
    ax.invert_yaxis()
    for bar, val in zip(bars, data['avg_wind_kph']):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}', va='center', fontsize=9)
    plt.tight_layout()
    return figure

def plot_air_quality(df, top_n=10):
    data = air_quality_by_country(df, top_n)
    figure, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(data['country'], data['avg_PM2.5'], color='darkorange')
    ax.set_xlabel('Average PM2.5')
    ax.set_title(f'Top {top_n} Countries with Worst Air Quality')
    ax.invert_yaxis()
    for bar, val in zip(bars, data['avg_PM2.5']):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}', va='center', fontsize=9)
    plt.tight_layout()
    return figure

def plot_conditions(df):
    data = condition_distribution(df)
    figure, ax = plt.subplots(figsize=(8, 8))
    ax.pie(data['count'], autopct='%1.1f%%', startangle=140,
           pctdistance=0.85)
    ax.legend(data['condition'], title="Conditions",
              loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title('Most Common Weather Conditions')
    plt.tight_layout()
    return figure