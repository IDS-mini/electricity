import pandas as pd
import numpy as np
from datetime import timedelta
from xgboost import XGBRegressor


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
        self.data = wind.join(consumption).tz_localize(tz='UTC')

    def forecast(self, n_days=3):
        SMA_WINDOW = 168  # Window size for simple moving average
        # Create a dataframe with hour date range from next UTC hour to n_days in the future
        now_ceil = pd.Timestamp.now(tz='UTC').ceil(freq='H')
        date_range = pd.date_range(
            start=now_ceil-timedelta(hours=SMA_WINDOW), end=now_ceil+timedelta(days=n_days), freq="H")
        future_df = pd.DataFrame(
            {'datetime': date_range}).set_index('datetime')
        future_df = future_df.join(self.data)
        future_df = create_features(future_df)
        features = ['Wind_MWh', 'Consumption_MWh', 'dayofyear', 'hour', 'dayofweek', 'quarter', 'month', 'year',
                    'c_lag1', 'c_lag2', 'c_lag3', 'w_lag1', 'w_lag2', 'w_lag3']  # These should be the same as used in modelling!!!
        future_df['price'] = self._model.predict(future_df[features])
        future_df['SMA'] = future_df['price'].rolling(SMA_WINDOW).mean()
        future_df['value'] = future_df['price'] / future_df['SMA']
        future_df['recommendation'] = future_df['value'].apply(
            get_recommendation)
        RETURNED_FEATURES = ['value', 'recommendation']
        future_df = future_df[now_ceil:][RETURNED_FEATURES].reset_index()
        return future_df.to_dict(orient='records')

    def fake_forecast(self):
        # Create a dataframe with date range
        now_ceil = pd.Timestamp.now(tz='UTC').ceil(freq='H')
        date_range = pd.date_range(
            start=now_ceil, end=now_ceil+timedelta(days=3), freq="H")
        df = pd.DataFrame({'datetime': date_range})
        df['value'] = np.random.normal(1, 1, len(df))

        df['recommendation'] = df['value'].apply(get_recommendation)
        return df.to_dict("records")
