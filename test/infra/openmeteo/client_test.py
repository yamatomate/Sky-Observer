from logging import getLogger
from unittest.mock import MagicMock, patch

from sky_observer.infra.openmeteo.client import (
  LocationResponse,
  OpenMeteoClient,
  WeatherDataResponse,
)

logger = getLogger(__name__)


@patch("sky_observer.infra.openmeteo.client.openmeteo_requests")
def test_weather_data_response_success(mock_client):
  # Arrange
  mock_current = MagicMock()

  mock_var_temperature = MagicMock()
  mock_var_humidity = MagicMock()
  mock_var_cloud_cover = MagicMock()
  mock_var_precipitation = MagicMock()
  mock_var_weather_code = MagicMock()
  mock_var_wind_speed = MagicMock()
  mock_var_visibility = MagicMock()
  mock_var_is_day = MagicMock()

  mock_var_temperature.Value.return_value = 25
  mock_var_humidity.Value.return_value = 50
  mock_var_cloud_cover.Value.return_value = 75
  mock_var_precipitation.Value.return_value = 0
  mock_var_weather_code.Value.return_value = 1
  mock_var_wind_speed.Value.return_value = 10
  mock_var_visibility.Value.return_value = 10000
  mock_var_is_day.Value.return_value = 1

  mock_current.Variables.side_effect = [
    mock_var_temperature,
    mock_var_humidity,
    mock_var_cloud_cover,
    mock_var_precipitation,
    mock_var_weather_code,
    mock_var_wind_speed,
    mock_var_visibility,
    mock_var_is_day,
  ]

  mock_single_response = MagicMock()
  mock_single_response.Current.return_value = mock_current

  mock_client_instance = MagicMock()
  mock_client_instance.weather_api.return_value = [mock_single_response]

  mock_client.Client.return_value = mock_client_instance

  client = OpenMeteoClient()

  # Act
  response = client.get_weather(latitude=0.0, longitude=0.0)

  # Assert
  assert response is not None
  assert isinstance(response, WeatherDataResponse)
  assert response.temperature_c == 25
  assert response.humidity_pct == 50
  assert response.cloud_cover_pct == 75
  assert response.precipitation_mm == 0
  assert response.weather_code == 1
  assert response.weather_description == "Predom. claro"
  assert response.wind_speed_kmh == 10
  assert response.visibility_m == 10000
  assert response.is_day is True


@patch("sky_observer.infra.openmeteo.client.niquests_cache.CachedSession")
def test_search_location_success(mock_cached_session_cls):
  # Arrange
  mock_http_response = MagicMock()

  mock_http_response.json.return_value = {
    "results": [
      {
        "latitude": -5.0892,
        "longitude": -42.8019,
        "elevation": 72.0,
        "country": "Brasil",
        "country_code": "BR",
        "timezone": "America/Fortaleza",
        "population": 868755,
      }
    ]
  }

  mock_http_response.raise_for_status.return_value = None

  mock_session_instance = MagicMock()
  mock_session_instance.get.return_value = mock_http_response

  mock_cached_session_cls.return_value = mock_session_instance

  client = OpenMeteoClient()

  # Act
  response = client.search_location(name="Teresina")

  # Assert
  assert response is not None
  assert isinstance(response, LocationResponse)
  assert response.name == "Teresina"
  assert response.latitude == -5.0892
  assert response.longitude == -42.8019
  assert response.elevation == 72.0
  assert response.country == "Brasil"
  assert response.country_code == "BR"
  assert response.timezone == "America/Fortaleza"
  assert response.population == 868755
