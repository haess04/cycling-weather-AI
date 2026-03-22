import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import RouteType


client = TestClient(app)


class TestRootEndpoint:
    def test_root_returns_info(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "features" in data
        assert "road" in data["features"]
        assert "mtb" in data["features"]
        assert "city" in data["features"]


class TestWeatherEndpoint:
    def test_weather_valid_coords_default_road(self):
        """Test with Warsaw coordinates - default route_type is road"""
        response = client.get("/weather?latitude=52.2297&longitude=21.0122")
        assert response.status_code == 200
        data = response.json()
        assert "location" in data
        assert "days" in data
        assert data["route_type"] == "road"
        assert len(data["days"]) == 7
        assert "bike_score" in data["days"][0]
        assert "bike_condition" in data["days"][0]

    def test_weather_with_mtb_route_type(self):
        """Test with MTB route type"""
        response = client.get(
            "/weather?latitude=52.2297&longitude=21.0122&route_type=mtb"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["route_type"] == "mtb"
        assert len(data["days"]) == 7

    def test_weather_with_city_route_type(self):
        """Test with city route type"""
        response = client.get(
            "/weather?latitude=52.2297&longitude=21.0122&route_type=city"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["route_type"] == "city"
        assert len(data["days"]) == 7

    def test_weather_mtb_higher_score_than_road(self):
        """MTB should generally score higher than road in same conditions"""
        road_response = client.get(
            "/weather?latitude=52.2297&longitude=21.0122&route_type=road"
        )
        mtb_response = client.get(
            "/weather?latitude=52.2297&longitude=21.0122&route_type=mtb"
        )

        road_data = road_response.json()
        mtb_data = mtb_response.json()

        # Sum of scores for comparison
        road_total = sum(day["bike_score"] for day in road_data["days"])
        mtb_total = sum(day["bike_score"] for day in mtb_data["days"])

        # MTB should be more forgiving (higher or equal scores)
        assert mtb_total >= road_total

    def test_weather_invalid_latitude_high(self):
        response = client.get("/weather?latitude=100&longitude=0")
        assert response.status_code == 422

    def test_weather_invalid_latitude_low(self):
        response = client.get("/weather?latitude=-100&longitude=0")
        assert response.status_code == 422

    def test_weather_invalid_longitude_high(self):
        response = client.get("/weather?latitude=0&longitude=200")
        assert response.status_code == 422

    def test_weather_invalid_longitude_low(self):
        response = client.get("/weather?latitude=0&longitude=-200")
        assert response.status_code == 422

    def test_weather_missing_params(self):
        response = client.get("/weather")
        assert response.status_code == 422


class TestWarsawEndpoint:
    def test_warsaw_returns_data(self):
        response = client.get("/weather/warsaw")
        assert response.status_code == 200
        data = response.json()
        assert "days" in data
        assert data["route_type"] == "road"  # default
        assert len(data["days"]) == 7

    def test_warsaw_with_mtb(self):
        response = client.get("/weather/warsaw?route_type=mtb")
        assert response.status_code == 200
        data = response.json()
        assert data["route_type"] == "mtb"


class TestWeatherPostEndpoint:
    def test_post_valid_coords(self):
        response = client.post(
            "/weather", json={"latitude": 52.2297, "longitude": 21.0122}
        )
        assert response.status_code == 200
        data = response.json()
        assert "days" in data
        assert len(data["days"]) == 7

    def test_post_with_route_type(self):
        response = client.post(
            "/weather",
            json={"latitude": 52.2297, "longitude": 21.0122, "route_type": "mtb"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["route_type"] == "mtb"
