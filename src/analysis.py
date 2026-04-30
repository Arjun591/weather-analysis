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
    """
    Improved forecast using seasonal weighted moving average
    Accounts for seasonal patterns and recent trends
    """
    df = df.copy()
    df = df.sort_values('last_updated')
    df['month'] = df['last_updated'].dt.month
    df['day_of_year'] = df['last_updated'].dt.dayofyear

    forecasts = {}
    last_date = df['last_updated'].max()

    for col in ['temperature_celsius', 'humidity', 'wind_kph']:
        series = df[['last_updated', 'month', 'day_of_year', col]].dropna()
        if len(series) < 30:
            continue

        future = []
        for i in range(1, days + 1):
            future_date = last_date + pd.Timedelta(days=i)
            future_month = future_date.month
            future_doy = future_date.timetuple().tm_yday

            # Get historical data for same month
            same_month = series[series['month'] == future_month][col]

            # Get recent 30 days data
            recent_30 = series.tail(30)[col]

            # Get recent 7 days data
            recent_7 = series.tail(7)[col]

            if len(same_month) == 0:
                base = series[col].mean()
            else:
                # Weighted average:
                # 50% weight to same month historical average
                # 30% weight to recent 30 days average
                # 20% weight to recent 7 days average
                seasonal_avg = same_month.mean()
                recent_30_avg = recent_30.mean()
                recent_7_avg = recent_7.mean()

                base = (0.5 * seasonal_avg +
                        0.3 * recent_30_avg +
                        0.2 * recent_7_avg)

            # Add small daily variation based on historical std
            daily_std = series[col].std()
            variation = daily_std * 0.1 * np.sin(i * np.pi / 3.5)

            predicted = round(float(base + variation), 1)
            future.append((future_date, predicted))

        forecasts[col] = future

    return forecasts


def forecast_for_date(df, target_date):
    """
    Improved forecast for a specific date
    Uses seasonal patterns from historical data
    """
    df = df.copy()
    df = df.sort_values('last_updated')
    target = pd.to_datetime(target_date)
    target_month = target.month

    results = {}
    for col in ['temperature_celsius', 'humidity', 'wind_kph', 'pressure_mb']:
        series = df[['last_updated', col]].dropna()
        if len(series) < 7:
            continue

        df_col = series.copy()
        df_col['month'] = df_col['last_updated'].dt.month

        # Same month historical average
        same_month = df_col[df_col['month'] == target_month][col]

        # Recent data
        recent_30 = df_col.tail(30)[col]
        recent_7  = df_col.tail(7)[col]

        if len(same_month) == 0:
            predicted = round(float(df_col[col].mean()), 1)
        else:
            seasonal_avg   = same_month.mean()
            recent_30_avg  = recent_30.mean()
            recent_7_avg   = recent_7.mean()

            # How far in the future is the target date?
            days_ahead = (target - df['last_updated'].max()).days

            # For near future give more weight to recent data
            # For far future give more weight to seasonal data
            if days_ahead <= 7:
                predicted = round(float(
                    0.3 * seasonal_avg +
                    0.3 * recent_30_avg +
                    0.4 * recent_7_avg
                ), 1)
            elif days_ahead <= 30:
                predicted = round(float(
                    0.4 * seasonal_avg +
                    0.4 * recent_30_avg +
                    0.2 * recent_7_avg
                ), 1)
            else:
                predicted = round(float(
                    0.7 * seasonal_avg +
                    0.2 * recent_30_avg +
                    0.1 * recent_7_avg
                ), 1)

        results[col] = predicted

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