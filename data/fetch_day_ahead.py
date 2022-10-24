from bs4 import BeautifulSoup as bs
import requests
from datetime import datetime,timedelta
import pandas as pd
import numpy as np


def get_dayahead():
    tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%d.%m.%Y')
    URL = f"https://transparency.entsoe.eu/transmission-domain/r2/dayAheadPrices/show?name=&defaultValue=false&viewType=TABLE&areaType=BZN&atch=false&dateTime.dateTime={tomorrow_str}+00:00|UTC|DAY&biddingZone.values=CTY|10YFI-1--------U!BZN|10YFI-1--------U&resolution.values=PT60M&dateTime.timezone=UTC&dateTime.timezone_input=UTC"

    try:
        with requests.get(URL) as r:
            soup = bs(r.content, "html.parser")
            table = soup.tbody.text
    except:
        return None

    rows = table.replace('\n\n','').replace(':00\n',':00,').splitlines()
    data = []
    for row in rows:
        data.append([tomorrow + timedelta(hours=int(row[:2])), row.split(',')[1]])
    df = pd.DataFrame(data=data, columns=['datetime','price']).set_index('datetime')
    df['price'] = df['price'].replace('-',np.nan).astype('float')
    df = df.dropna()
    df = df.tz_localize('UTC')
    # datetime: Time in UTC
    # price: Day-ahead price EUR/MWh
    return df


#print(get_dayahead())