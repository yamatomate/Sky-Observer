import logging
from math import cos, radians
from typing import Literal

from skyfield.timelib import Time

from sky_observer.db.location_service import LocationService
from sky_observer.infra.openmeteo.client import OpenMeteoClient
from sky_observer.infra.skyfield.client import (
  AllObjectResponse,
  SkyFieldClient,
  SkyFieldClientError,
)
from sky_observer.services.models import (
  CelestialObject,
  CityResult,
  ConditionsResult,
  PlanetVisibility,
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

    # Calcular seeing dinamicamente baseado no score (escala de 1 a 8)
    seeing_val = max(1, min(8, round((score / 100.0) * 8)))

    # Calcular fase da lua em porcentagem de iluminação
    moon_info = self.skyfield_client.get_moon_phase(self.skyfield_client.get_time_now())
    illumination_pct = 50.0 * (1.0 - cos(radians(moon_info.phase)))

    # SkyMetrics espera strings descritivas
    metrics = SkyMetrics(
      cloud_cover=f"{weather.cloud_cover_pct:.0f}",
      seeing=str(seeing_val),
      humidity=f"{weather.humidity_pct:.0f}",
      moon_phase=f"{illumination_pct:.0f}",
    )

    # Obter os objetos celestes usando as coordenadas reais da localização
    planets_response = self.skyfield_client.get_all_observable_objects(
      latitude=lat, longitude=lon
    )

    planets_visibility: list[PlanetVisibility] = []
    if not isinstance(planets_response, SkyFieldClientError):
      for obj in planets_response.objects:
        # Determinar a cor do status para a UI
        if not obj.visible:
          p_status = "red"
        elif obj.altitude > 15.0:
          p_status = "green"
        else:
          p_status = "yellow"

        # Detalhes do objeto formatados conforme esperado pela view
        detail_str = f"Alt. {obj.altitude:.0f}°  ·  Az. {obj.azimuth:.0f}°"

        planets_visibility.append(
          PlanetVisibility(
            name=obj.name,
            detail=detail_str,
            status=p_status,
          )
        )
    else:
      logger.error(f"Erro ao obter planetas observáveis: {planets_response.message}")

    return ConditionsResult(
      location=name,
      score=int(score),
      status=status,
      title=title,
      subtitle=subtitle,
      metrics=metrics,
      planets=planets_visibility,
    )

  # SkyField
  def get_visible_objects(
    self, lat: float, lon: float, horario: Time
  ) -> list[CelestialObject]:
    if horario is None:
      horario = self.skyfield_client.get_time_now()

    objetos_celestes: AllObjectResponse | SkyFieldClientError = (
      self.skyfield_client.get_all_observable_objects(
        horario=horario, latitude=lat, longitude=lon
      )
    )

    if isinstance(objetos_celestes, SkyFieldClientError):
      return []

    celestiais: list[CelestialObject] = []
    for x in objetos_celestes.objects:
      celestiais.append(
        CelestialObject(
          name=x.name,
          details=f"Alt. {x.altitude:.2f}º Az. {x.azimuth:.2f}º",
          status="green" if x.visible else "red",
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
