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
        # Try to get latest saved prediction, if not succeed, create a new XGBOOST Prediction
        latest = predictor.get_latest_forecast()
        if latest is not None:
            return latest
        return predictor.forecast(add_dayahead=True)
    else:
        return predictor.fake_forecast()

@app.get("/about", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/planning", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("planning.html", {"request": request})
