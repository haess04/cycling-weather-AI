# 🚴 Cycling Weather AI

AI-Developed Project.

A smart weather application for cyclists with route-type-specific scoring algorithms (road, MTB, city).
<img width="2851" height="1504" alt="image" src="https://github.com/user-attachments/assets/0139ac88-7127-483a-ac1a-cbc791ecd7f9" />


## ✨ Features

- **7-day weather forecast** using Open-Meteo API (free, no API key required)
- **3 route types** with dedicated scoring algorithms:
  - 🛣️ **Road** - sensitive to wind and rain (high speeds)
  - 🏔️ **MTB** - tolerates mud and light rain (better traction)
  - 🏙️ **City** - most forgiving (short trips, easy to bail)
- **Smart scoring algorithm (0-100)** based on temperature, precipitation, and wind
- **Geolocation** - automatically detects user location
- **Dark mode** - toggle between light and dark themes
- **Day details** - click any card to see detailed weather info

## 🏗️ Architecture

```
cycling_weather_ai/
├── backend/              # FastAPI + Python
│   ├── app/
│   │   ├── main.py       # FastAPI application & endpoints
│   │   ├── models.py     # Pydantic models + RouteType enum
│   │   └── weather.py    # 3 scoring algorithms for route types
│   ├── tests/            # 33 pytest tests
│   └── requirements.txt
├── frontend/             # HTML + Tailwind CSS + JS
│   ├── index.html
│   └── app.js
└── README.md
```

## 🚀 Quick Start

### Requirements
- Python 3.9+

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```
API runs at `http://localhost:8001`

### Frontend
```bash
cd frontend
python -m http.server 3000
```
App runs at `http://localhost:3000`

## 📊 Scoring Algorithms

### Road Cycling
| Parameter | Penalty |
|-----------|---------|
| Temp < 5°C | -40 pts |
| Rain | -1.5x % precipitation |
| Wind > 35 km/h | -40 pts |

### MTB
| Parameter | Penalty |
|-----------|---------|
| Temp < 0°C | -30 pts |
| Rain | -0.2-0.8x % precipitation |
| Wind > 40 km/h | -25 pts |

### City/Commute
| Parameter | Penalty |
|-----------|---------|
| Temp < -5°C | -25 pts |
| Rain | -0.6x % precipitation |
| Wind > 45 km/h | -20 pts |

**Score Categories:**
- 🟢 80-100: Excellent
- 🟢 60-79: Good  
- 🟡 40-59: Moderate
- 🟠 20-39: Poor
- 🔴 0-19: Bad

## 🛠️ Tech Stack

- **Backend:** FastAPI, Pydantic, httpx, pytest
- **Frontend:** HTML5, Tailwind CSS (CDN), Vanilla JS, Lucide Icons
- **Weather API:** Open-Meteo (free, no API key)

## 📝 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /weather?lat={}&lon={}&route_type={road\|mtb\|city}` | Weather for location |
| `GET /weather/warsaw?route_type={}` | Weather for Warsaw (default) |
| `POST /weather` | Weather (JSON body) |
| `GET /docs` | Swagger UI documentation |

## 🧪 Testing

```bash
cd backend
pytest -v
```

**33 tests** covering:
- Scoring algorithms for all route types
- API endpoints
- Data validation
