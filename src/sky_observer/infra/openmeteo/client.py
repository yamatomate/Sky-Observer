import logging
from dataclasses import dataclass

import niquests_cache
import openmeteo_requests
from urllib3.util import Retry

from .utils import WMO_CODES

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WeatherData:
  temperature_c: float
  humidity_pct: float
  cloud_cover_pct: float
  precipitation_mm: float
  weather_code: int
  weather_description: str
  wind_speed_kmh: float


class OpenMeteoClient:
  base_url: str
  client: openmeteo_requests.Client

  def __init__(self, base_url: str = "https://api.open-meteo.com/v1/forecast"):
    self.base_url = base_url
    retries_config = Retry(
      total=3, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504]
    )
    cached_session = niquests_cache.CachedSession(
      ".cache", expire_after=300, retries=retries_config
    )
    self.client = openmeteo_requests.Client(session=cached_session)

  def get_weather(self, latitude: float, longitude: float) -> WeatherData | None:
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
    for i in range(6):
      var = current.Variables(i)
      if var is None:
        logger.warning("Resposta do OpenMeteo com variáveis faltando no índice %d", i)
        return None
      values.append(float(var.Value()))

    code = int(values[4])
    return WeatherData(
      temperature_c=values[0],
      humidity_pct=values[1],
      cloud_cover_pct=values[2],
      precipitation_mm=values[3],
      weather_code=code,
      weather_description=WMO_CODES.get(code, "Desconhecido"),
      wind_speed_kmh=values[5],
    )
