from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import numpy as np
from datetime import timedelta

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/app/static"), name="static")
templates = Jinja2Templates(directory="src/app/templates")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/plan")
def plan():
    # Create a dataframe with date range
    now_ceil = pd.Timestamp.now(tz='UTC').ceil(freq='H')
    date_range = pd.date_range(
        start=now_ceil, end=now_ceil+timedelta(days=3), freq="H")
    df = pd.DataFrame({'date': date_range})
    df['value'] = np.random.normal(1, 1, len(df))

    def get_recommendation(x):
        if x > 1.3:
            return '-'
        elif x < -0.7:
            return '+'
        else:
            return '0'
    df['recommendation'] = df['value'].apply(get_recommendation)
    return df.to_dict("records")
