import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from src.analysis import (temperature_by_country, temperature_trends,
                           humidity_by_country, precipitation_trends,
                           wind_by_country, air_quality_by_country,
                           condition_distribution, correlation_matrix,
                           seasonal_analysis, year_over_year)

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

def plot_correlation_heatmap(df):
    """Heatmap showing correlation between weather variables"""
    corr = correlation_matrix(df)
    figure, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)
    plt.colorbar(im, ax=ax)
    labels = ['Temp', 'Humidity', 'Wind', 'Pressure',
              'Precip', 'Cloud', 'Visibility', 'UV Index']
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_yticklabels(labels)
    # Add correlation values inside cells
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f'{corr.iloc[i, j]:.2f}',
                    ha='center', va='center', fontsize=8,
                    color='black')
    ax.set_title('Correlation Heatmap of Weather Variables')
    plt.tight_layout()
    return figure

def plot_seasonal_analysis(df):
    """Bar chart showing weather patterns by season"""
    data = seasonal_analysis(df)
    figure, axes = plt.subplots(2, 2, figsize=(12, 8))
    figure.suptitle('Seasonal Weather Analysis', fontsize=14, fontweight='bold')

    seasons = data['season']
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']

    # Temperature
    axes[0,0].bar(seasons, data['temperature_celsius'], color=colors)
    axes[0,0].set_title('Avg Temperature (°C)')
    axes[0,0].set_ylabel('°C')

    # Humidity
    axes[0,1].bar(seasons, data['humidity'], color=colors)
    axes[0,1].set_title('Avg Humidity (%)')
    axes[0,1].set_ylabel('%')

    # Precipitation
    axes[1,0].bar(seasons, data['precip_mm'], color=colors)
    axes[1,0].set_title('Avg Precipitation (mm)')
    axes[1,0].set_ylabel('mm')

    # Wind
    axes[1,1].bar(seasons, data['wind_kph'], color=colors)
    axes[1,1].set_title('Avg Wind Speed (kph)')
    axes[1,1].set_ylabel('kph')

    plt.tight_layout()
    return figure

def plot_year_over_year(df):
    """Year over year temperature comparison"""
    data = year_over_year(df)
    figure, ax = plt.subplots(figsize=(10, 5))
    x = range(len(data['year']))
    ax.fill_between(data['year'], data['min_temp'], data['max_temp'],
                    alpha=0.2, color='orange', label='Min-Max Range')
    ax.plot(data['year'], data['avg'], marker='o', color='orange',
            linewidth=2, label='Avg Temperature')
    ax.set_xlabel('Year')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Year over Year Temperature Comparison')
    ax.legend()
    ax.set_xticks(data['year'])
    plt.tight_layout()
    return figure
def plot_forecast(df, days=7):
    """Plot forecast for next N days - 3 separate clean charts"""
    from src.analysis import forecast_weather
    forecasts = forecast_weather(df, days)

    figure, axes = plt.subplots(3, 1, figsize=(10, 9))
    figure.suptitle(f'Weather Forecast — Next {days} Days',
                    fontsize=13, fontweight='bold', y=1.01)

    cols   = ['temperature_celsius', 'humidity', 'wind_kph']
    titles = ['Temperature (°C)', 'Humidity (%)', 'Wind Speed (kph)']
    colors = ['tomato', 'steelblue', 'mediumseagreen']

    for i, (col, title, color) in enumerate(zip(cols, titles, colors)):
        ax = axes[i]
        if col not in forecasts or not forecasts[col]:
            ax.text(0.5, 0.5, 'Not enough data',
                    ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title)
            continue

        dates  = [d.strftime('%b %d') for d, _ in forecasts[col]]
        values = [v for _, v in forecasts[col]]

        ax.plot(dates, values, marker='o', color=color,
                linewidth=2, markersize=6)
        ax.fill_between(range(len(dates)), values,
                        alpha=0.15, color=color)
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, fontsize=9)
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_ylabel(title.split(' ')[1], fontsize=9)
        ax.grid(axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Value labels — above each point, no overlap
        for j, val in enumerate(values):
            ax.annotate(f'{val}',
                        xy=(j, val),
                        xytext=(0, 10),
                        textcoords='offset points',
                        ha='center', fontsize=8, color=color)

    plt.tight_layout()
    return figure
def plot_health_index(df, top_n=15):
    """Plot top countries by weather health index"""
    from src.analysis import weather_health_index
    data = weather_health_index(df).head(top_n)

    figure, ax = plt.subplots(figsize=(12, 7))

    colors = []
    for score in data['health_index']:
        if score >= 80:
            colors.append('#2ecc71')
        elif score >= 60:
            colors.append('#f1c40f')
        elif score >= 40:
            colors.append('#e67e22')
        else:
            colors.append('#e74c3c')

    bars = ax.barh(data['country'], data['health_index'], color=colors)
    ax.set_xlabel('Health Index Score (0-100)')
    ax.set_title('Weather Health Index by Country')
    ax.invert_yaxis()
    ax.axvline(x=80, color='green', linestyle='--', alpha=0.5, label='Excellent (80)')
    ax.axvline(x=60, color='gold', linestyle='--', alpha=0.5, label='Good (60)')
    ax.axvline(x=40, color='orange', linestyle='--', alpha=0.5, label='Moderate (40)')
    ax.legend()

    for bar, (_, row) in zip(bars, data.iterrows()):
        ax.text(bar.get_width() + 0.5,
                bar.get_y() + bar.get_height()/2,
                f"{row['health_index']} {row['grade']}",
                va='center', fontsize=8)

    plt.tight_layout()
    return figure

def plot_climate_change(df):
    """Plot warming and cooling countries"""
    from src.analysis import climate_change_detector
    _, warming, cooling = climate_change_detector(df)

    figure, axes = plt.subplots(1, 2, figsize=(14, 7))
    figure.suptitle('Climate Change Detector', fontsize=14, fontweight='bold')

    # Warming countries
    if not warming.empty:
        axes[0].barh(warming['country'], warming['change_per_year'], color='tomato')
        axes[0].set_title('Top Warming Countries')
        axes[0].set_xlabel('Temperature Change per Year (°C)')
        axes[0].invert_yaxis()
        for i, (_, row) in enumerate(warming.iterrows()):
            axes[0].text(row['change_per_year'] + 0.01,
                         i, f"+{row['change_per_year']}°C/yr",
                         va='center', fontsize=8)

    # Cooling countries
    if not cooling.empty:
        axes[1].barh(cooling['country'], abs(cooling['change_per_year']), color='steelblue')
        axes[1].set_title('Top Cooling Countries')
        axes[1].set_xlabel('Temperature Change per Year (°C)')
        axes[1].invert_yaxis()
        for i, (_, row) in enumerate(cooling.iterrows()):
            axes[1].text(abs(row['change_per_year']) + 0.01,
                         i, f"{row['change_per_year']}°C/yr",
                         va='center', fontsize=8)

    plt.tight_layout()
    return figure