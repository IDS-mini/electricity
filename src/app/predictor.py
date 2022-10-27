import sys
sys.path.insert(1, '../../')
import pandas as pd
import numpy as np
import datetime
from xgboost import XGBRegressor
from utils import fetch_weather
from utils import fetch_day_ahead
from utils import fetch_consumption


def create_features(df):
    """
    Create time series features based on time series index.
    """
    df = df.copy()
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['quarter'] = df.index.quarter
    df['month'] = df.index.month
    df['year'] = df.index.year
    df['dayofyear'] = df.index.dayofyear
    df['dayofmonth'] = df.index.day
    df['weekofyear'] = df.index.isocalendar().week
    return df


def get_recommendation(x):
    if x > 1.2:
        return '-'
    elif x < 0.8:
        return '+'
    else:
        return '0'


class Predictor:
    def __init__(self):
        self._model = XGBRegressor()
        self._model.load_model('models/xgboost_model.ubj')
        wind = pd.read_parquet('future_data/wind.parquet')
        consumption = pd.read_parquet('future_data/consumption.parquet')
        weather = pd.read_parquet('future_data/weather.parquet')
        self.data = wind.join(consumption).join(weather).tz_localize(tz='UTC')

    def add_fresh_data(self, df):
        #fetch 7 days weather history + 2 days forecast
        weather_fetched = fetch_weather.get_7days_and_forecast_2days()
        #fetch 14 days consumption history
        consumption_fetched = fetch_consumption.get_consumption_trimmed(datetime.datetime.now()-datetime.timedelta(days=14), datetime.datetime.now())
        df.update(weather_fetched)
        df.update(consumption_fetched)
        return df

    def add_dayahead_prices(self, df):
        #fetch prices for tomorrow and add on top of predicted prices
        dayahead_fetched = fetch_day_ahead.get_dayahead()
        df.update(dayahead_fetched)
        return df

    def forecast(self, add_dayahead, n_days=3):
        SMA_WINDOW = 168  # Window size for simple moving average
        now_ceil = pd.Timestamp.now(tz='UTC').ceil(freq='H')
        # Add fresh data (consumption and weather)
        self.data = self.add_fresh_data(self.data)
        date_range = pd.date_range(
            start=now_ceil-datetime.timedelta(hours=SMA_WINDOW), end=now_ceil+datetime.timedelta(days=n_days), freq="H")
        future_df = pd.DataFrame(
            {'datetime': date_range}).set_index('datetime')
        future_df = future_df.join(self.data)
        future_df = create_features(future_df)
        features = ['Wind_MWh','Consumption_MWh','pressure','rain','humidity','temperature','wind',
                    'dayofyear', 'hour', 'dayofweek', 'quarter', 'month', 'year',
                    'c_lag1','c_lag2','c_lag3','w_lag1','w_lag2','w_lag3','pr_lag1','pr_lag2','pr_lag3',
                    'rain_lag1','rain_lag2','rain_lag3','hum_lag1','hum_lag2','hum_lag3',
                    'temp_lag1','temp_lag2','temp_lag3','win_lag1','win_lag2','win_lag3'] 
                    # These features should be the same as used in modelling!!!
        future_df['price'] = self._model.predict(future_df[features])
        # Add day-ahead prices on top of predictions if wanted
        if add_dayahead:
            future_df = self.add_dayahead_prices(future_df)
        # Create a dataframe with hour date range from next UTC hour to n_days in the future
        future_df['SMA'] = future_df['price'].rolling(SMA_WINDOW).mean()
        future_df['value'] = future_df['price'] / future_df['SMA']
        future_df['recommendation'] = future_df['value'].apply(get_recommendation)
        RETURNED_FEATURES = ['value', 'recommendation']
        future_df = future_df[now_ceil:][RETURNED_FEATURES].reset_index()
        future_df.to_csv('forecast_data/forecasts.csv')
        return future_df.to_dict(orient='records')

    def fake_forecast(self):
        # Create a dataframe with date range
        now_ceil = pd.Timestamp.now(tz='UTC').ceil(freq='H')
        date_range = pd.date_range(
            start=now_ceil, end=now_ceil+datetime.timedelta(days=3), freq="H")
        df = pd.DataFrame({'datetime': date_range})
        df['value'] = np.random.normal(1, 1, len(df))
        df['recommendation'] = df['value'].apply(get_recommendation)
        return df.to_dict('records')

    def get_latest_forecast(self):
        try:
            df = pd.read_csv('forecast_data/forecasts.csv')
            return df.to_dict('records')
        except:
            return None
