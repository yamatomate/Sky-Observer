# pyright: reportPrivateUsage=false
from logging import getLogger
from unittest.mock import MagicMock, patch

import pytest

from sky_observer.infra.openmeteo.client import LocationResponse
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
