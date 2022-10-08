import requests
import io
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
apikey = os.getenv('FING_API_KEY')

def get_consumption(datetime_start, datetime_end):
    '''Input time format: python datetime in UTC
    Returns: Pandas DataFrame'''

    start_time = datetime_start.isoformat(timespec="seconds") + 'Z'
    end_time = datetime_end.isoformat(timespec="seconds") + 'Z'
    params = {'start_time': start_time, 'end_time': end_time}
    url = 'https://api.fingrid.fi/v1/variable/124/events/csv'

    try:
        req = requests.get(url, headers={"x-api-key":apikey}, params=params)
    except:
        return None

    df = pd.read_csv(io.StringIO(req.content.decode('utf-8')))
    df['c'] = ''
    df['d'] = ''
    df = df.loc[:,['start_time', 'end_time', 'c', 'd', 'value']]

    return df

#test printing:
#print(get_consumption(datetime.datetime.now()-datetime.timedelta(days=1), datetime.datetime.now()))