# pyright: reportPrivateUsage=false
from logging import getLogger
from unittest.mock import MagicMock, patch

import pytest

from sky_observer.infra.openmeteo.client import LocationResponse, WeatherDataResponse
from sky_observer.infra.skyfield.client import AllObjectResponse, MoonDetail, ObjectCelest
from sky_observer.services.models import CityResult
from sky_observer.services.observation_service import ObservationService

logger = getLogger(__name__)


@patch("sky_observer.services.observation_service.SkyFieldClient")
@patch("sky_observer.services.observation_service.LocationService")
@patch("sky_observer.services.observation_service.OpenMeteoClient")
def test_search_location(
  MockOpenMeteoClient: MagicMock,
  _MockLocationService: MagicMock,
  _MockSkyFieldClient: MagicMock,
):
  # Arrange
  mock_openmeteo_instance = MockOpenMeteoClient.return_value
  mock_openmeteo_instance.search_location.return_value = LocationResponse(
    name="FAKE",
    latitude=-25.4284,
    longitude=-49.2733,
    elevation=934.0,
    country="TalvezBrasil",
    country_code="BR",
    timezone="America/Sao_Paulo",
    population=1879355,
  )

  observation_service = ObservationService()

  # Act
  result = observation_service.search_location("Curitiba")

  # Assert
  assert result is not None
  assert result == CityResult(
    name="FAKE",
    latitude=-25.4284,
    longitude=-49.2733,
    country="TalvezBrasil",
  )
  mock_openmeteo_instance.search_location.assert_called_once_with("Curitiba")


@pytest.mark.parametrize(
  "cloud, humidity, visibility, expected_score",
  [
    (0.0, 50.0, 10000.0, 100.0),  # Condições perfeitas
    (100.0, 100.0, 0.0, 0.0),  # Condições péssimas
    (50.0, 80.0, 5000.0, 50.0),  # Condições intermediárias
  ],
)
@patch("sky_observer.services.observation_service.SkyFieldClient")
@patch("sky_observer.services.observation_service.LocationService")
@patch("sky_observer.services.observation_service.OpenMeteoClient")
def test_calculate_score(
  _MockOpenMeteoClient: MagicMock,
  _MockLocationService: MagicMock,
  _MockSkyFieldClient: MagicMock,
  cloud: float,
  humidity: float,
  visibility: float,
  expected_score: float,
):
  # Arrange
  service = ObservationService()

  # Act
  score = service._calculate_score(cloud, humidity, visibility)

  # Assert
  assert score == expected_score


@pytest.mark.parametrize(
  "score, expected_status",
  [
    (75.0, "good"),
    (80.0, "good"),
    (45.0, "fair"),
    (50.0, "fair"),
    (44.9, "bad"),
    (0.0, "bad"),
  ],
)
@patch("sky_observer.services.observation_service.SkyFieldClient")
@patch("sky_observer.services.observation_service.LocationService")
@patch("sky_observer.services.observation_service.OpenMeteoClient")
def test_score_to_status(
  _MockOpenMeteoClient: MagicMock,
  _MockLocationService: MagicMock,
  _MockSkyFieldClient: MagicMock,
  score: float,
  expected_status: str,
):
  # Arrange
  service = ObservationService()

  # Act
  status = service._score_to_status(score)

  # Assert
  assert status == expected_status


@patch("sky_observer.services.observation_service.SkyFieldClient")
@patch("sky_observer.services.observation_service.LocationService")
@patch("sky_observer.services.observation_service.OpenMeteoClient")
def test_get_conditions(
  MockOpenMeteoClient: MagicMock,
  _MockLocationService: MagicMock,
  MockSkyFieldClient: MagicMock,
):
  # Arrange
  mock_openmeteo_instance = MockOpenMeteoClient.return_value
  mock_openmeteo_instance.get_weather.return_value = WeatherDataResponse(
    temperature_c=22.5,
    humidity_pct=50.0,
    cloud_cover_pct=10.0,
    precipitation_mm=0.0,
    weather_code=0,
    weather_description="Céu limpo",
    wind_speed_kmh=12.0,
    visibility_m=10000.0,
    is_day=True,
  )

  mock_skyfield_instance = MockSkyFieldClient.return_value
  mock_skyfield_instance.get_moon_phase.return_value = MoonDetail(
    phase=90.0,
    phase_name="Quarto Crescente",
  )
  mock_skyfield_instance.get_all_observable_objects.return_value = AllObjectResponse(
    objects=[
      ObjectCelest(
        name="Saturno",
        type="planeta",
        visible=True,
        altitude=62.0,
        azimuth=188.0,
      ),
      ObjectCelest(
        name="Vênus",
        type="planeta",
        visible=False,
        altitude=-10.0,
        azimuth=270.0,
      ),
    ]
  )

  observation_service = ObservationService()

  # Act
  result = observation_service.get_conditions(-23.5505, -46.6333, "São Paulo")

  # Assert
  assert result is not None
  assert result.location == "São Paulo"
  assert result.status == "good"
  assert result.score == 94  # cloud_score = 90 * 0.6 = 54, humidity_score = 100 * 0.15 = 15, visibility_score = 100 * 0.25 = 25. Total = 94.
  assert result.metrics.cloud_cover == "10"
  assert result.metrics.humidity == "50"
  assert result.metrics.seeing == "8"  # round((94 / 100.0) * 8) = 8
  assert result.metrics.moon_phase == "50"  # 50 * (1 - cos(rad(90))) = 50 * 1 = 50
  
  # Assert planets visibility mapping
  assert len(result.planets) == 2
  assert result.planets[0].name == "Saturno"
  assert result.planets[0].detail == "Alt. 62°  ·  Az. 188°"
  assert result.planets[0].status == "green"  # visible & alt > 15

  assert result.planets[1].name == "Vênus"
  assert result.planets[1].detail == "Alt. -10°  ·  Az. 270°"
  assert result.planets[1].status == "red"  # visible is False

  mock_openmeteo_instance.get_weather.assert_called_once_with(-23.5505, -46.6333)
  mock_skyfield_instance.get_all_observable_objects.assert_called_once_with(
    latitude=-23.5505, longitude=-46.6333
  )
