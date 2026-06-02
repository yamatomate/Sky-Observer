import logging
from typing import Literal

import skyfield
import skyfield.units
from skyfield.relativity import C

from sky_observer.db.location_service import LocationService
from sky_observer.infra.openmeteo.client import OpenMeteoClient
from sky_observer.infra.skyfield.client import AllObjectResponse, SkyFieldClient
from sky_observer.services.models import (
  CelestialObject,
  CityResult,
  ConditionsResult,
  SkyMetrics,
)

logger = logging.getLogger(__name__)


class ObservationService:
  location_service: LocationService
  openmeteo_client: OpenMeteoClient
  skyfield_client: SkyFieldClient

  def __init__(self):
    self.location_service = LocationService()
    self.openmeteo_client = OpenMeteoClient()
    self.skyfield_client = SkyFieldClient()

  # Openmeteo + SkyField
  def get_conditions(self, lat: float, lon: float, name: str) -> ConditionsResult:
    """Obtém as condições atuais para a localização.

    Args:
      lat: Latitude da localização.
      lon: Longitude da localização.
      name: Nome da localização.

    Returns:
      ConditionsResult com as condições atuais.

      ConditionsResult:
        location: Nome da localização.
        score: Score de observação (0-100).
        status: Status da observação (good, fair, bad).
        title: Título descritivo.
        subtitle: Subtítulo descritivo.
        metrics: Métricas do céu.
          cloud_cover: Cobertura de nuvens (0-100).
          seeing: Seeing (0-100).
          humidity: Umidade (0-100).
          moon_phase: Fase da lua (0-100).
        planets: Planetas visíveis.
    """
    # Openmeteo
    weather = self.openmeteo_client.get_weather(lat, lon)
    if not weather:
      raise ValueError(
        "Não foi possivel obter dados meteorológicos para esta localização"
      )

    score = self._calculate_score(
      cloud=weather.cloud_cover_pct,
      humidity=weather.humidity_pct,
      visibility=weather.visibility_m,
    )

    status = self._score_to_status(score)

    titles = {
      "good": ("Céu Excelente", "Condições perfeitas para observar o cosmos hoje!"),
      "fair": (
        "Céu Regular",
        "Algumas nuvens ou umidade podem atrapalhar a observação.",
      ),
      "bad": ("Céu Ruim", "Condições desfavoráveis. Melhor planejar para outro dia."),
    }
    title, subtitle = titles[status]

    # SkyField
    metrics = SkyMetrics(
      cloud_cover=...,
      seeing=...,
      humidity=...,
      moon_phase=...,
    )

    # planets = self.skyfield_client.planetas

    # Depois da uma olhada no documento que o Thiago escreveu em:
    # ui/docs/INTEGRATION_GUIDE.md
    return ConditionsResult(
      location=name,
      score=int(score),
      status=status,
      title=title,
      subtitle=subtitle,
      metrics=metrics,
      planets=planets,
    )

  # SkyField
  def get_visible_objects(self, lat: float, lon: float) -> list[CelestialObject]:
    self.skyfield_client.set_location(lat, lon)
    obejtos_celestes: list[AllObjectResponse] = (
      self.skyfield_client.get_all_observable_objects()
    )
    celestiais: list[CelestialObject] = []
    print(obejtos_celestes)
    for x in obejtos_celestes:
      if x.altitude.degrees > skyfield.units.Angle(degrees=1).degrees:
        celestiais.append(
          CelestialObject(
            name=x.name,
            icon="",
            type="planeta",
            details=f"Alt. {x.altitude.degrees:.2f}º Az. {x.azimuth.degrees:.2f}º",
          )
        )
    return celestiais

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


if __name__ == "__main__":
  teste = ObservationService()
  objetos = teste.get_visible_objects(lat=0, lon=0)
  print(objetos)
