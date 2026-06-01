import logging
from typing import Literal

from sky_observer.db.location_service import LocationService
from sky_observer.infra.openmeteo.client import OpenMeteoClient
from sky_observer.infra.skyfield.client import SkyFieldClient
from sky_observer.services.models import (
  CelestialObject,
  CityResult,
  ConditionsResult,
)

logger = logging.getLogger(__name__)


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

  def search_location(self, query: str) -> CityResult | None:
    """Busca uma cidade pelo nome usando o OpenMeteoClient.

    Args:
      query: Nome da cidade a ser buscada.

    Returns:
      CityResult com os dados da cidade encontrada ou None se não for encontrada.
    """
    try:
      result = self.openmeteo_client.search_location(query)

      if result is not None:
        return CityResult(
          name=result.name,
          latitude=result.latitude,
          longitude=result.longitude,
          country=result.country,
        )

      return None
    except Exception as e:
      logger.exception(f"Failed to search location: {e}")
      pass
    pass

  def _calculate_score(self, cloud: float, humidity: float, visibility: float) -> float:
    """Calcula um score astronômico de 0 a 100 para as condições do céu.

    A pontuação é a soma ponderada de três fatores:
    1. Cobertura de nuvens (peso de 60%): Redução linear (0% nuvens = 60 pts; 100% nuvens = 0 pts).
    2. Umidade (peso de 15%): Nota máxima de 15 pts para umidade < 60%. Acima disso,
       decai 2.5% para cada 1% de umidade extra, zerando em 100% de umidade.
    3. Visibilidade (peso de 25%): Escala linear de 0 a 10 km (10.000m). Visibilidades
       de 10 km ou mais atingem a pontuação máxima de 25 pts.
    """
    cloud_score = (100 - cloud) * 0.60

    if humidity < 60:
      humidity_score = 100.0
    else:
      humidity_score = max(0.0, 100.0 - (humidity - 60) * 2.5)

    humidity_score *= 0.15
    visibility_score = min(100.0, (visibility / 10000.0) * 100.0) * 0.25

    return cloud_score + humidity_score + visibility_score

  def _score_to_status(self, score: float) -> Literal["good", "fair", "bad"]:
    """
    Converte o score de observação em um status descritivo:
    - "good": score >= 75
    - "fair": 45 <= score < 75
    - "bad": score < 45
    """
    if score >= 75:
      return "good"
    elif score >= 45:
      return "fair"
    return "bad"
