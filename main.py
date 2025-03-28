# Updated backend logic: uses incident time to now, not future prediction

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import datetime
import math
import subprocess
import os
import xarray as xr
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

object_profiles = {
    "Person_Adult_LifeJacket": {"drag_factor": 0.8},
    "Person_Adult_NoLifeJacket": {"drag_factor": 1.1},
    "Person_Adolescent_LifeJacket": {"drag_factor": 0.9},
    "Person_Child_LifeJacket": {"drag_factor": 1.0},
    "Catamaran": {"drag_factor": 0.4},
    "Hobby_Cat": {"drag_factor": 0.5},
    "Fishing_Trawler": {"drag_factor": 0.2},
    "RHIB": {"drag_factor": 0.6},
    "SUP_Board": {"drag_factor": 1.2},
    "Windsurfer": {"drag_factor": 1.3},
    "Kayak": {"drag_factor": 1.1}
}

def fetch_hourly_copernicus_data(lat, lon, start_time, end_time, username, password):
    lat_min = lat - 0.1
    lat_max = lat + 0.1
    lon_min = lon - 0.1
    lon_max = lon + 0.1

    date_min = start_time.strftime("%Y-%m-%d %H:%M:%S")
    date_max = end_time.strftime("%Y-%m-%d %H:%M:%S")

    motu_cmd = [
        "python", "-m", "motuclient",
        "--motu", "https://nrt.cmems-du.eu/motu-web/Motu",
        "--service-id", "GLOBAL_ANALYSISFORECAST_PHY_001_024-TDS",
        "--product-id", "cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
        "--longitude-min", str(lon_min), "--longitude-max", str(lon_max),
        "--latitude-min", str(lat_min), "--latitude-max", str(lat_max),
        "--date-min", date_min, "--date-max", date_max,
        "--depth-min", "0.5", "--depth-max", "0.5",
        "--variable", "uo", "--variable", "vo",
        "--out-dir", "./data", "--out-name", "drift_data.nc",
        "--user", username, "--pwd", password
    ]

    subprocess.run(motu_cmd, check=True)
    return "./data/drift_data.nc"

def integrate_hourly_drift(nc_file, lat, lon, hours, drag):
    ds = xr.open_dataset(nc_file)
    coords = (lat, lon)
    for i in range(min(int(abs(hours)), len(ds.time))):
        index = i if hours > 0 else len(ds.time) - 1 - i
        uo = ds["uo"].isel(time=index).interp(latitude=coords[0], longitude=coords[1]).values.item()
        vo = ds["vo"].isel(time=index).interp(latitude=coords[0], longitude=coords[1]).values.item()

        dx = uo * 3.6 * drag
        dy = vo * 3.6 * drag

        delta_lat = dy / 111.0
        delta_lon = dx / (111.0 * math.cos(math.radians(coords[0])))

        coords = (coords[0] + delta_lat, coords[1] + delta_lon)
    ds.close()
    return round(coords[0], 6), round(coords[1], 6)

def recommend_search_pattern(hours, drift_km):
    if abs(hours) < 1 and drift_km < 2:
        return "Sector Search", "Use when position is recent and precise."
    elif abs(hours) < 3 and drift_km < 8:
        return "Expanding Square", "Covers moderate uncertainty zones."
    else:
        return "Parallel Sweep", "Large coverage when drift is wide."

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request,
                  latitude: float = Form(...),
                  longitude: float = Form(...),
                  date: str = Form(...),
                  time: str = Form(...),
                  object_type: str = Form(...),
                  life_jacket: str = Form(None),
                  age_group: str = Form(None)):

    if object_type == "Person":
        object_key = f"Person_{age_group}_{'LifeJacket' if life_jacket == 'Yes' else 'NoLifeJacket'}"
    else:
        object_key = object_type.replace(" ", "_")

    incident_datetime = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    now = datetime.datetime.utcnow()
    delta_hours = (now - incident_datetime).total_seconds() / 3600.0

    cmems_user = os.getenv("CMEMS_USER")
    cmems_pwd = os.getenv("CMEMS_PWD")

    try:
        nc_file = fetch_hourly_copernicus_data(latitude, longitude, incident_datetime, now, cmems_user, cmems_pwd)
        drag = object_profiles.get(object_key, {"drag_factor": 1.0})["drag_factor"]
        new_lat, new_lon = integrate_hourly_drift(nc_file, latitude, longitude, delta_hours, drag)

        drift_km = math.sqrt((new_lat - latitude)**2 + (new_lon - longitude)**2) * 111.0
    except Exception as e:
        print("[ERROR] Fallback to default drift:", e)
        drag = object_profiles.get(object_key, {"drag_factor": 1.0})["drag_factor"]
        uo, vo = 0.3, 0.2
        dx = uo * 3.6 * abs(delta_hours) * drag
        dy = vo * 3.6 * abs(delta_hours) * drag
        delta_lat = dy / 111.0
        delta_lon = dx / (111.0 * math.cos(math.radians(latitude)))
        new_lat = round(latitude + delta_lat, 6)
        new_lon = round(longitude + delta_lon, 6)
        drift_km = math.sqrt(dx**2 + dy**2)

    pattern, reason = recommend_search_pattern(delta_hours, drift_km)

    return templates.TemplateResponse("result.html", {
        "request": request,
        "orig_lat": latitude,
        "orig_lon": longitude,
        "new_lat": new_lat,
        "new_lon": new_lon,
        "object_type": object_type,
        "life_jacket": life_jacket,
        "age_group": age_group,
        "search_pattern": pattern,
        "pattern_reason": reason,
        "elapsed_hours": round(delta_hours, 2),
        "drift_km": round(drift_km, 2)
    })
