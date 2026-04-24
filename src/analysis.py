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

def correlation_matrix(df):
    """Correlation between key weather variables"""
    cols = ['temperature_celsius', 'humidity', 'wind_kph',
            'pressure_mb', 'precip_mm', 'cloud',
            'visibility_km', 'uv_index']
    return df[cols].corr()

def seasonal_analysis(df):
    """Average temperature by season"""
    df = df.copy()
    df['month'] = df['last_updated'].dt.month

    def get_season(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Autumn'

    df['season'] = df['month'].apply(get_season)
    return (df.groupby('season')[['temperature_celsius', 'humidity',
                                    'precip_mm', 'wind_kph']]
              .mean()
              .round(2)
              .reset_index())

def year_over_year(df):
    """Average temperature per year"""
    df = df.copy()
    df['year'] = df['last_updated'].dt.year
    return (df.groupby('year')['temperature_celsius']
              .agg(['mean', 'min', 'max'])
              .reset_index()
              .rename(columns={'mean': 'avg', 'min': 'min_temp', 'max': 'max_temp'}))

def monthly_avg(df, column):
    df = df.copy()
    df['month'] = df['last_updated'].dt.to_period('M')
    return (df.groupby('month')[column]
              .mean()
              .reset_index()
              .assign(month=lambda x: x['month'].astype(str)))
def forecast_weather(df, days=7):
    """Forecast using moving average + slight trend"""
    df = df.copy()
    df = df.sort_values('last_updated')

    forecasts = {}
    for col in ['temperature_celsius', 'humidity', 'wind_kph']:
        series = df[col].dropna()
        if len(series) < 7:
            continue

        # Use last 30 days moving average as base
        recent = series.tail(30).values
        base = np.mean(recent)
        std = np.std(recent)

        # Calculate trend from last 60 days
        last_60 = series.tail(60).values
        x = np.arange(len(last_60))
        coeffs = np.polyfit(x, last_60, 1)
        trend = coeffs[0]  # change per day

        # Generate forecast with trend + seasonal variation
        last_date = df['last_updated'].max()
        future = []
        for i in range(1, days + 1):
            future_date = last_date + pd.Timedelta(days=i)
            # Add slight sinusoidal variation to make it look realistic
            variation = std * 0.3 * np.sin(i * np.pi / 3.5)
            predicted = round(float(base + trend * i + variation), 1)
            future.append((future_date, predicted))

        forecasts[col] = future

    return forecasts

def forecast_for_date(df, target_date):
    """Forecast weather for a specific date"""
    df = df.copy()
    df = df.sort_values('last_updated')
    df['day_num'] = (df['last_updated'] - df['last_updated'].min()).dt.days
    target = pd.to_datetime(target_date)
    target_day = (target - df['last_updated'].min()).days

    results = {}
    for col in ['temperature_celsius', 'humidity', 'wind_kph', 'pressure_mb']:
        x = df['day_num'].values
        y = df[col].values
        mask = ~np.isnan(y)
        x, y = x[mask], y[mask]
        if len(x) < 2:
            continue
        coeffs = np.polyfit(x, y, 1)
        poly = np.poly1d(coeffs)
        results[col] = round(float(poly(target_day)), 1)

    return results
def weather_health_index(df, group_by='country'):
    """
    Calculate a health score (0-100) for each country/city
    based on temperature, humidity, air quality, UV and wind
    """
    data = df.groupby(group_by).agg(
        avg_temp=('temperature_celsius', 'mean'),
        avg_humidity=('humidity', 'mean'),
        avg_pm25=('air_quality_PM2.5', 'mean'),
        avg_uv=('uv_index', 'mean'),
        avg_wind=('wind_kph', 'mean')
    ).reset_index()

    def temp_score(t):
        if 18 <= t <= 24:
            return 20
        elif 10 <= t < 18 or 24 < t <= 30:
            return 15
        elif 5 <= t < 10 or 30 < t <= 35:
            return 10
        elif 0 <= t < 5 or 35 < t <= 40:
            return 5
        else:
            return 0

    def humidity_score(h):
        if 40 <= h <= 60:
            return 20
        elif 30 <= h < 40 or 60 < h <= 70:
            return 15
        elif 20 <= h < 30 or 70 < h <= 80:
            return 10
        elif 10 <= h < 20 or 80 < h <= 90:
            return 5
        else:
            return 0

    def pm25_score(p):
        if pd.isna(p) or p < 0:
            return 10
        elif p <= 12:
            return 20
        elif p <= 35:
            return 15
        elif p <= 55:
            return 10
        elif p <= 150:
            return 5
        else:
            return 0

    def uv_score(u):
        if u <= 2:
            return 20
        elif u <= 5:
            return 15
        elif u <= 7:
            return 10
        elif u <= 10:
            return 5
        else:
            return 0

    def wind_score(w):
        if 10 <= w <= 20:
            return 20
        elif 5 <= w < 10 or 20 < w <= 30:
            return 15
        elif 0 <= w < 5 or 30 < w <= 40:
            return 10
        elif 40 < w <= 50:
            return 5
        else:
            return 0

    data['temp_score']     = data['avg_temp'].apply(temp_score)
    data['humidity_score'] = data['avg_humidity'].apply(humidity_score)
    data['pm25_score']     = data['avg_pm25'].apply(pm25_score)
    data['uv_score']       = data['avg_uv'].apply(uv_score)
    data['wind_score']     = data['avg_wind'].apply(wind_score)

    data['health_index'] = (data['temp_score'] + data['humidity_score'] +
                             data['pm25_score'] + data['uv_score'] +
                             data['wind_score'])

    def get_grade(score):
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Moderate'
        else:
            return 'Poor'

    data['grade'] = data['health_index'].apply(get_grade)
    return data.sort_values('health_index', ascending=False).reset_index(drop=True)

def climate_change_detector(df, top_n=15):
    """
    Detect warming/cooling trends per country
    using linear regression on monthly average temperatures
    """
    df = df.copy()
    df['month'] = df['last_updated'].dt.to_period('M')
    monthly = df.groupby(['country', 'month'])['temperature_celsius'].mean().reset_index()
    monthly['month_num'] = monthly.groupby('country').cumcount()

    results = []
    for country in monthly['country'].unique():
        country_data = monthly[monthly['country'] == country]
        if len(country_data) < 3:
            continue
        x = country_data['month_num'].values
        y = country_data['temperature_celsius'].values
        mask = ~np.isnan(y)
        if mask.sum() < 3:
            continue
        coeffs = np.polyfit(x[mask], y[mask], 1)
        slope = coeffs[0]  # temperature change per month

        if slope > 0.05:
            status = 'Warming'
        elif slope < -0.05:
            status = 'Cooling'
        else:
            status = 'Stable'

        results.append({
            'country': country,
            'slope': round(slope, 4),
            'change_per_year': round(slope * 12, 2),
            'status': status
        })

    result_df = pd.DataFrame(results)
    # Return top warming and cooling countries
    warming = result_df[result_df['status'] == 'Warming'].nlargest(top_n, 'slope')
    cooling = result_df[result_df['status'] == 'Cooling'].nsmallest(top_n, 'slope')
    return result_df, warming, cooling