
from fmiopendata.wfs import download_stored_query
import datetime
import pandas as pd

def get_last_7_days_weather():
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(days=7)
    start_time = start_time.isoformat(timespec="seconds") + "Z"
    end_time = end_time.isoformat(timespec="seconds") + "Z"

    try:
        obs = download_stored_query("fmi::observations::weather::multipointcoverage",
                                args=["bbox=24.94,60.19,24.97,60.21",
                                    "timeseries=True",
                                    "starttime=" + start_time,
                                    "endtime=" + end_time])
        #check if the correct dict is present
        obs.data['Helsinki Kumpula']
    except:
        return None

    df = pd.DataFrame()
    df['datetime'] = obs.data['Helsinki Kumpula']['times']
    df['temperature'] = obs.data['Helsinki Kumpula']['t2m']['values']
    df['pressure'] = obs.data['Helsinki Kumpula']['p_sea']['values']
    df['humidity'] = obs.data['Helsinki Kumpula']['rh']['values']
    df['wind'] = obs.data['Helsinki Kumpula']['ws_10min']['values']
    df['rain'] = obs.data['Helsinki Kumpula']['r_1h']['values']
    df = df.set_index('datetime')

    return df



def get_forecast_2_days():
    try:
        obs = download_stored_query("fmi::forecast::hirlam::surface::point::multipointcoverage",
                                args=["place=Helsinki",
                                    "timeseries=True"])
        #check if the correct dict is present
        obs.data['Helsinki']
    except:
        return None

    df = pd.DataFrame()
    df['datetime'] = obs.data['Helsinki']['times']
    df['temperature'] = obs.data['Helsinki']['Temperature']['values']
    df['pressure'] = obs.data['Helsinki']['Pressure']['values']
    df['humidity'] = obs.data['Helsinki']['Humidity']['values']
    df['wind'] = obs.data['Helsinki']['WindSpeedMS']['values']
    df['rain'] = obs.data['Helsinki']['PrecipitationAmount']['values']
    df = df.set_index('datetime')
    
    return df

#Test printings:
#print(get_forecast_2_days())
#print(get_last_7_days_weather())