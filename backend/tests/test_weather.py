import pytest
from app.weather import (
    calculate_bike_score,
    calculate_road_score,
    calculate_mtb_score,
    calculate_city_score,
    get_bike_condition,
    get_recommendation,
    get_weekday_name,
    parse_weather_code,
    BikeCondition,
    RouteType,
)


class TestCalculateRoadScore:
    """Tests for road cycling scoring - sensitive to wind and rain."""

    def test_perfect_road_conditions(self):
        """Ideal road conditions: 18°C, 0% rain, 10 km/h wind"""
        score = calculate_road_score(18, 0, 10)
        assert score == 100

    def test_road_strong_wind(self):
        """Road cycling is very sensitive to wind"""
        score_calm = calculate_road_score(20, 0, 10)
        score_windy = calculate_road_score(20, 0, 40)
        assert score_calm > score_windy + 25  # Big penalty for wind

    def test_road_rain_sensitive(self):
        """Road bikes have less traction in rain"""
        score_no_rain = calculate_road_score(20, 0, 10)
        score_rain = calculate_road_score(20, 50, 10)
        assert score_no_rain > score_rain + 50  # 1.5x penalty


class TestCalculateMtbScore:
    """Tests for MTB scoring - tolerates rain and wind better."""

    def test_mtb_handles_rain_better(self):
        """MTB handles rain much better than road"""
        mtb_score = calculate_mtb_score(20, 50, 10)
        road_score = calculate_road_score(20, 50, 10)
        assert mtb_score > road_score

    def test_mtb_tolerates_wind_better(self):
        """MTB is less affected by wind"""
        mtb_score = calculate_mtb_score(20, 0, 40)
        road_score = calculate_road_score(20, 0, 40)
        assert mtb_score > road_score


class TestCalculateCityScore:
    """Tests for city/commute scoring - most tolerant."""

    def test_city_most_tolerant(self):
        """City cycling is most tolerant of bad weather"""
        city_score = calculate_city_score(20, 50, 40)
        road_score = calculate_road_score(20, 50, 40)
        mtb_score = calculate_mtb_score(20, 50, 40)
        # All should be more tolerant than road
        assert city_score > road_score
        assert mtb_score > road_score


class TestGetBikeCondition:
    def test_excellent(self):
        assert get_bike_condition(90) == BikeCondition.EXCELLENT
        assert get_bike_condition(80) == BikeCondition.EXCELLENT

    def test_good(self):
        assert get_bike_condition(79) == BikeCondition.GOOD
        assert get_bike_condition(60) == BikeCondition.GOOD

    def test_moderate(self):
        assert get_bike_condition(59) == BikeCondition.MODERATE
        assert get_bike_condition(40) == BikeCondition.MODERATE

    def test_poor(self):
        assert get_bike_condition(39) == BikeCondition.POOR
        assert get_bike_condition(20) == BikeCondition.POOR

    def test_bad(self):
        assert get_bike_condition(19) == BikeCondition.BAD
        assert get_bike_condition(0) == BikeCondition.BAD


class TestGetRecommendation:
    def test_returns_string_for_each_type(self):
        for route_type in RouteType:
            for condition in BikeCondition:
                rec = get_recommendation(condition, route_type)
                assert isinstance(rec, str)
                assert len(rec) > 0

    def test_different_recommendations_for_same_condition(self):
        """Same condition should have different advice for different route types"""
        road_rec = get_recommendation(BikeCondition.MODERATE, RouteType.ROAD)
        mtb_rec = get_recommendation(BikeCondition.MODERATE, RouteType.MTB)
        assert road_rec != mtb_rec


class TestGetWeekdayName:
    def test_valid_dates(self):
        assert get_weekday_name("2024-01-01") == "Poniedziałek"
        assert get_weekday_name("2024-01-02") == "Wtorek"
        assert get_weekday_name("2024-01-07") == "Niedziela"


class TestParseWeatherCode:
    def test_known_codes(self):
        assert parse_weather_code(0) == "Czyste niebo"
        assert parse_weather_code(95) == "Burza"

    def test_unknown_code(self):
        assert parse_weather_code(999) == "Nieznane warunki"


class TestCalculateBikeScoreWithRouteType:
    """Tests for the unified scoring function with route type parameter."""

    def test_default_is_road(self):
        """Default route type should be road"""
        score_default = calculate_bike_score(20, 30, 30)
        score_road = calculate_bike_score(20, 30, 30, RouteType.ROAD)
        assert score_default == score_road

    def test_mtb_more_forgiving(self):
        """MTB should score higher than road in bad conditions"""
        score_road = calculate_bike_score(5, 60, 35, RouteType.ROAD)
        score_mtb = calculate_bike_score(5, 60, 35, RouteType.MTB)
        assert score_mtb > score_road

    def test_city_most_forgiving(self):
        """City should score highest in bad conditions"""
        score_road = calculate_bike_score(5, 60, 35, RouteType.ROAD)
        score_mtb = calculate_bike_score(5, 60, 35, RouteType.MTB)
        score_city = calculate_bike_score(5, 60, 35, RouteType.CITY)
        assert score_city >= score_mtb > score_road
