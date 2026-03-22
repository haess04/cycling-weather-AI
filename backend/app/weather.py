import httpx
from typing import List, Dict, Any
from datetime import datetime
from .models import DayForecast, BikeCondition, RouteType


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def calculate_road_score(
    temp_avg: float, precipitation_prob: float, wind_speed_avg: float
) -> int:
    """
    Road cycling scoring - sensitive to wind and rain.
    High speeds on road bikes make wind and rain more problematic.
    """
    score = 100

    # Temperature scoring (road cyclists often ride longer, need comfort)
    if temp_avg < 0:
        score -= 60
    elif temp_avg < 5:
        score -= 40
    elif temp_avg < 10:
        score -= 25
    elif temp_avg > 35:
        score -= 60
    elif temp_avg > 30:
        score -= 40
    elif temp_avg > 25:
        score -= 15

    # Precipitation (road bikes have less traction, more dangerous)
    score -= precipitation_prob * 1.5

    # Wind (very sensitive - high speed + wind = dangerous)
    if wind_speed_avg > 45:
        score -= 50
    elif wind_speed_avg > 35:
        score -= 40
    elif wind_speed_avg > 25:
        score -= 25
    elif wind_speed_avg > 15:
        score -= 10

    return max(0, min(100, int(score)))


def calculate_mtb_score(
    temp_avg: float, precipitation_prob: float, wind_speed_avg: float
) -> int:
    """
    MTB scoring - tolerates rain and wind better.
    Mountain bikes have better grip and are ridden at lower speeds.
    """
    score = 100

    # Temperature (MTB riders are tougher, but extreme temps still matter)
    if temp_avg < -10:
        score -= 50
    elif temp_avg < 0:
        score -= 30
    elif temp_avg < 5:
        score -= 15
    elif temp_avg > 35:
        score -= 50
    elif temp_avg > 30:
        score -= 25

    # Precipitation (MTB handles rain better - actually fun in light rain)
    if precipitation_prob > 80:
        score -= precipitation_prob * 0.8
    elif precipitation_prob > 50:
        score -= precipitation_prob * 0.5
    else:
        score -= precipitation_prob * 0.2

    # Wind (less sensitive than road - lower speeds, more shelter)
    if wind_speed_avg > 50:
        score -= 35
    elif wind_speed_avg > 40:
        score -= 25
    elif wind_speed_avg > 30:
        score -= 15

    return max(0, min(100, int(score)))


def calculate_city_score(
    temp_avg: float, precipitation_prob: float, wind_speed_avg: float
) -> int:
    """
    City/commute scoring - most tolerant.
    Short trips, can bail easily, slower speeds.
    """
    score = 100

    # Temperature (commuters are hardy - short trips)
    if temp_avg < -15:
        score -= 40
    elif temp_avg < -5:
        score -= 25
    elif temp_avg < 0:
        score -= 10
    elif temp_avg > 40:
        score -= 40
    elif temp_avg > 35:
        score -= 20

    # Precipitation (can take shelter, short trip = less exposure)
    score -= precipitation_prob * 0.6

    # Wind (less sensitive - urban areas have wind blocks)
    if wind_speed_avg > 55:
        score -= 30
    elif wind_speed_avg > 45:
        score -= 20
    elif wind_speed_avg > 35:
        score -= 10

    return max(0, min(100, int(score)))


def calculate_bike_score(
    temp_avg: float,
    precipitation_prob: float,
    wind_speed_avg: float,
    route_type: RouteType = RouteType.ROAD,
) -> int:
    """
    Calculate bike riding score from 0-100 based on weather conditions and route type.

    Args:
        temp_avg: Average temperature in Celsius
        precipitation_prob: Precipitation probability (0-100%)
        wind_speed_avg: Average wind speed in km/h
        route_type: Type of cycling (road, mtb, city)
    """
    if route_type == RouteType.MTB:
        return calculate_mtb_score(temp_avg, precipitation_prob, wind_speed_avg)
    elif route_type == RouteType.CITY:
        return calculate_city_score(temp_avg, precipitation_prob, wind_speed_avg)
    else:  # Default to ROAD
        return calculate_road_score(temp_avg, precipitation_prob, wind_speed_avg)


def get_bike_condition(score: int) -> BikeCondition:
    """Convert score to condition category."""
    if score >= 80:
        return BikeCondition.EXCELLENT
    elif score >= 60:
        return BikeCondition.GOOD
    elif score >= 40:
        return BikeCondition.MODERATE
    elif score >= 20:
        return BikeCondition.POOR
    else:
        return BikeCondition.BAD


def get_recommendation(condition: BikeCondition, route_type: RouteType) -> str:
    """Get human-readable recommendation based on condition and route type."""
    recommendations = {
        RouteType.ROAD: {
            BikeCondition.EXCELLENT: "Idealna pogoda na szosę! Ciesz się jazdą.",
            BikeCondition.GOOD: "Dobra pogoda, można jechać szosą.",
            BikeCondition.MODERATE: "Uważaj - warunki średnie dla szosy.",
            BikeCondition.POOR: "Zła pogoda na szosę - za dużo wiatr/deszcz.",
            BikeCondition.BAD: "Zostań w domu lub wybierz MTB/miasto.",
        },
        RouteType.MTB: {
            BikeCondition.EXCELLENT: "Świetnie! MTB będzie frajdą.",
            BikeCondition.GOOD: "Dobre warunki na górską wycieczkę.",
            BikeCondition.MODERATE: "Można jechać, ale uważaj na błoto.",
            BikeCondition.POOR: "Trudne warunki, sprawdź trasę.",
            BikeCondition.BAD: "Zbyt niebezpieczne na MTB dzisiaj.",
        },
        RouteType.CITY: {
            BikeCondition.EXCELLENT: "Idealnie! Rowerem do pracy/szkoły.",
            BikeCondition.GOOD: "Dobra pogoda na miejskie przejażdżki.",
            BikeCondition.MODERATE: "Spokojnie, dasz radę dojechać.",
            BikeCondition.POOR: "Może warto wziąć tramwaj/autobus?",
            BikeCondition.BAD: "Dziś lepiej zostań w domu.",
        },
    }
    return recommendations[route_type][condition]


def get_weekday_name(date_str: str) -> str:
    """Get Polish weekday name from date string."""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    weekdays = [
        "Poniedziałek",
        "Wtorek",
        "Środa",
        "Czwartek",
        "Piątek",
        "Sobota",
        "Niedziela",
    ]
    return weekdays[date.weekday()]


def parse_weather_code(code: int) -> str:
    """Parse WMO weather code to description."""
    codes = {
        0: "Czyste niebo",
        1: "Pogodnie",
        2: "Częściowo zachmurzone",
        3: "Zachmurzone",
        45: "Mgła",
        48: "Mgła z szronem",
        51: "Lekka mżawka",
        53: "Umiarkowana mżawka",
        55: "Gęsta mżawka",
        61: "Lekki deszcz",
        63: "Umiarkowany deszcz",
        65: "Silny deszcz",
        71: "Lekki śnieg",
        73: "Umiarkowany śnieg",
        75: "Silny śnieg",
        77: "Ziarna śniegu",
        80: "Przelotne opady deszczu",
        81: "Umiarkowane przelotne opady",
        82: "Silne przelotne opady",
        85: "Przelotne opady śniegu",
        86: "Silne przelotne opady śniegu",
        95: "Burza",
        96: "Burza z gradem",
        99: "Silna burza z gradem",
    }
    return codes.get(code, "Nieznane warunki")


async def fetch_weather_data(latitude: float, longitude: float) -> Dict[str, Any]:
    """Fetch 7-day weather forecast from Open-Meteo API."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "weather_code",
        ],
        "timezone": "Europe/Warsaw",
        "forecast_days": 7,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(OPEN_METEO_URL, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()


def process_weather_data(
    data: Dict[str, Any], route_type: RouteType = RouteType.ROAD
) -> List[DayForecast]:
    """Process raw API data into DayForecast objects."""
    daily = data["daily"]
    days = []

    for i in range(len(daily["time"])):
        temp_max = daily["temperature_2m_max"][i]
        temp_min = daily["temperature_2m_min"][i]
        temp_avg = (temp_max + temp_min) / 2
        precip_prob = daily["precipitation_probability_max"][i] or 0
        wind_max = daily["wind_speed_10m_max"][i]
        wind_avg = wind_max * 0.7  # Estimate average from max

        score = calculate_bike_score(temp_avg, precip_prob, wind_avg, route_type)
        condition = get_bike_condition(score)

        day = DayForecast(
            date=daily["time"][i],
            weekday=get_weekday_name(daily["time"][i]),
            temperature_max=temp_max,
            temperature_min=temp_min,
            temperature_avg=round(temp_avg, 1),
            precipitation_probability=precip_prob,
            precipitation_sum=daily["precipitation_sum"][i] or 0,
            wind_speed_max=wind_max,
            wind_speed_avg=round(wind_avg, 1),
            weather_code=daily["weather_code"][i],
            bike_score=score,
            bike_condition=condition,
            recommendation=get_recommendation(condition, route_type),
            route_type=route_type,
        )
        days.append(day)

    return days
