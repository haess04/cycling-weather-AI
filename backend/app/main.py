from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from .models import WeatherResponse, CoordinatesRequest, RouteType
from .weather import fetch_weather_data, process_weather_data


app = FastAPI(
    title="Cycling Weather API",
    description="API for checking bike riding weather conditions",
    version="1.1.0",
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Cycling Weather API",
        "version": "1.1.0",
        "features": ["road", "mtb", "city"],
        "docs": "/docs",
        "endpoints": {
            "weather": "/weather?latitude={lat}&longitude={lon}&route_type={road|mtb|city}"
        },
    }


@app.get("/weather", response_model=WeatherResponse)
async def get_weather(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    route_type: RouteType = Query(RouteType.ROAD, description="Type of cycling route"),
):
    """
    Get 7-day weather forecast with bike riding conditions.

    - **latitude**: Latitude (-90 to 90)
    - **longitude**: Longitude (-180 to 180)
    - **route_type**: Type of cycling - road, mtb, or city (default: road)

    Returns weather data with bike score (0-100) and recommendations tailored to route type.
    """
    try:
        raw_data = await fetch_weather_data(latitude, longitude)
        days = process_weather_data(raw_data, route_type)

        return WeatherResponse(
            location=f"{latitude}, {longitude}",
            latitude=latitude,
            longitude=longitude,
            route_type=route_type,
            days=days,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching weather data: {str(e)}"
        )


@app.post("/weather", response_model=WeatherResponse)
async def get_weather_post(coords: CoordinatesRequest):
    """Get weather data via POST request with JSON body."""
    route_type = coords.route_type if coords.route_type else RouteType.ROAD
    return await get_weather(coords.latitude, coords.longitude, route_type)


# Default location: Warsaw, Poland
@app.get("/weather/warsaw", response_model=WeatherResponse)
async def get_warsaw_weather(
    route_type: RouteType = Query(RouteType.ROAD, description="Type of cycling route"),
):
    """Get weather for Warsaw, Poland (default location)."""
    return await get_weather(52.2297, 21.0122, route_type)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
