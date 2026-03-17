
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

VITE_TOKEN = os.getenv("MAPBOX_TOKEN")
import requests

app = FastAPI(title="Mapbox Driving-Traffic API")

# ✅ CORS (allows React frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://mapbox-react-neon.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Coordinates(BaseModel):
    lat: float
    lon: float


class RouteRequest(BaseModel):
    source: Coordinates
    destination: Coordinates


@app.post("/get_routes")
def get_routes_api(req: RouteRequest):
    src_lat, src_lon = req.source.lat, req.source.lon
    dest_lat, dest_lon = req.destination.lat, req.destination.lon

    url = f"https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{src_lon},{src_lat};{dest_lon},{dest_lat}"

    params = {
        "alternatives": "true",
        "geometries": "geojson",
        "overview": "full",
        "access_token": VITE_TOKEN
    }

    response = requests.get(url, params=params)
    data = response.json()

    # 🔍 Debug (optional)
    print("Mapbox response:", data)

    routes = data.get("routes", [])

    result = []
    for i, r in enumerate(routes[:5]):
        distance_km = r["distance"] / 1000
        duration_min = r["duration"] / 60
        coordinates = r["geometry"]["coordinates"]

        result.append({
            "route_number": i + 1,
            "distance_km": round(distance_km, 2),
            "duration_min": round(duration_min, 2),
            "num_points": len(coordinates),
            "coordinates": coordinates   # ✅ FULL route for drawing
        })

    return {
        "num_routes": len(result),
        "routes": result
    }