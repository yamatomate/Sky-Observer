from logging import getLogger
from unittest.mock import MagicMock, patch

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
