from sky_observer.db.location_service import LocationService
from sky_observer.infra.openmeteo.client import OpenMeteoClient
from sky_observer.infra.skyfield.client import SkyFieldClient

from sky_observer.services.models import (
  CelestialObject,
  CityResult,
  ConditionsResult,
)

class ObservationService:
  location_service: LocationService
  openmeteo_client: OpenMeteoClient
  skyfield_client: SkyFieldClient

  def __init__(self):
    self.location_service = LocationService()
    self.openmeteo_client = OpenMeteoClient()
    self.skyfield_client = SkyFieldClient(0.0, 0.0)

  # Openmeteo + SkyField
  def get_conditions(self, lat: float, lon: float, name: str) -> ConditionsResult:
    pass

  # SkyField
  def get_visible_objects(self, lat: float, lon: float) -> list[CelestialObject]:
    pass

  # Openmeteo + SkyField
  def get_object_detail(
    self, object_name: str, lat: float, lon: float
  ) -> ConditionsResult:
    pass

  # OpenMeteo
  def search_location(self, query: str) -> CityResult | None:
    pass

  # Formula que gera o score de 0-100
  def _calculate_score(self, cloud: float, humidity: float, visibility: float) -> int:
    pass

  # Converte o score em "good", "fair", "bad", segundo a camada de UI
  def _score_to_status(self, score: float) -> str:
    pass
