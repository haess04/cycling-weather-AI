from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class BikeCondition(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    BAD = "bad"


class RouteType(str, Enum):
    """Type of cycling route - affects weather scoring algorithm."""

    ROAD = "road"  # Road cycling - sensitive to wind, needs good conditions
    MTB = "mtb"  # Mountain biking - tolerates some rain and wind
    CITY = "city"  # City/commute - most tolerant, short trips


class DayForecast(BaseModel):
    date: str
    weekday: str
    temperature_max: float
    temperature_min: float
    temperature_avg: float
    precipitation_probability: float
    precipitation_sum: float
    wind_speed_max: float
    wind_speed_avg: float
    weather_code: int
    bike_score: int
    bike_condition: BikeCondition
    recommendation: str
    route_type: RouteType = RouteType.ROAD


class WeatherResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    route_type: RouteType
    days: List[DayForecast]


class CoordinatesRequest(BaseModel):
    latitude: float
    longitude: float
    route_type: Optional[RouteType] = RouteType.ROAD
