import logging
from dataclasses import dataclass
from typing import Any, cast

import niquests
import openmeteo_requests
from niquests.typing import QueryParameterType
from urllib3.util import Retry

from .utils import WMO_CODES

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WeatherDataResponse:
  temperature_c: float
  humidity_pct: float
  cloud_cover_pct: float
  precipitation_mm: float
  weather_code: int
  weather_description: str
  wind_speed_kmh: float
  visibility_m: float
  is_day: bool


@dataclass(frozen=True)
class LocationResponse:
  name: str
  latitude: float
  longitude: float
  elevation: float
  country: str
  country_code: str
  timezone: str
  population: int


class OpenMeteoClient:
  base_url: str
  session: niquests.Session
  client: openmeteo_requests.Client

  def __init__(
    self,
    base_url: str = "https://api.open-meteo.com/v1/forecast",
  ):
    self.base_url = base_url

    retries_config = Retry(
      total=3,
      backoff_factor=0.2,
      status_forcelist=[500, 502, 503, 504],
    )

    self.session = niquests.Session(retries=retries_config)
    self.client = openmeteo_requests.Client(session=self.session)

  def get_weather(
    self,
    latitude: float,
    longitude: float,
  ) -> WeatherDataResponse | None:
    try:
      responses = self.client.weather_api(
        self.base_url,
        params={
          "latitude": latitude,
          "longitude": longitude,
          "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "cloud_cover",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
            "visibility",
            "is_day",
          ],
        },
      )
    except Exception as e:
      logger.error("Falha ao consultar OpenMeteo: %s", e)
      return None

    if not responses:
      return None

    current = responses[0].Current()
    if current is None:
      return None

    values: list[float] = []

    for i in range(8):
      var = current.Variables(i)

      if var is None:
        logger.warning(
          "Resposta do OpenMeteo com variáveis faltando no índice %d",
          i,
        )
        return None

      values.append(float(var.Value()))

    code = int(values[4])

    return WeatherDataResponse(
      temperature_c=values[0],
      humidity_pct=values[1],
      cloud_cover_pct=values[2],
      precipitation_mm=values[3],
      weather_code=code,
      weather_description=WMO_CODES.get(code, "Desconhecido"),
      wind_speed_kmh=values[5],
      visibility_m=values[6],
      is_day=bool(values[7]),
    )

  def search_location(
    self,
    name: str,
  ) -> LocationResponse | None:
    try:
      params: QueryParameterType = {
        "name": name,
        "count": "1",
        "language": "pt",
        "format": "json",
      }

      response = self.session.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params=params,
      )

      response.raise_for_status()

      json_data = cast(dict[str, Any], response.json())
      results = json_data.get("results")

      if not results:
        return None

      result = results[0]

      return LocationResponse(
        name=result["name"],
        latitude=result["latitude"],
        longitude=result["longitude"],
        elevation=result["elevation"],
        country=result["country"],
        country_code=result["country_code"],
        timezone=result["timezone"],
        population=result.get("population", 0),
      )

    except Exception as e:
      logger.error("Falha ao buscar localização: %s", e)
      return None
