from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from predictor import Predictor

app = FastAPI()

predictor = Predictor()
ENABLE_MACHINE_LEARNING = True

app.mount("/static", StaticFiles(directory="src/app/static"), name="static")
templates = Jinja2Templates(directory="src/app/templates")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/plan")
def plan():
    if ENABLE_MACHINE_LEARNING:
        # XGBOOST Prediction
        return predictor.forecast()
    else:
        return predictor.fake_forecast()
