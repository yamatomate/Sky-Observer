# import datetime # Ruffs reclamando
import os
import sys
from dataclasses import dataclass
from typing import Any

# import skyfield # Ruffs reclamando
from skyfield import api
from skyfield.api import N, Timescale, W, load, wgs84
from skyfield.framelib import ecliptic_frame
from skyfield.timelib import Time


def _resolve_data_path(filename: str) -> str:
  """Resolve o caminho de arquivos de dados (.bsp) para dev e empacotado.

  No PyInstaller --onefile, o arquivo é extraído em sys._MEIPASS.
  Em dev, ele fica na raiz do projeto (CWD).
  """
  if getattr(sys, "frozen", False):
    return os.path.join(sys._MEIPASS, filename)
  return filename


@dataclass(frozen=True)
class ObjectCelest:
  name: str
  type: str
  visible: bool
  altitude: float
  azimuth: float


@dataclass(frozen=True)
class SearchObjectResponse:
  objeto: ObjectCelest


@dataclass(frozen=True)
class SkyFieldClientError:
  error: int
  message: str


@dataclass(frozen=True)
class AllObjectResponse:
  objects: list[ObjectCelest]


@dataclass(frozen=True)
class PlanetsResult:
  planets: Any


@dataclass(frozen=True)
class MoonDetail:
  phase: float
  phase_name: str


"""
Primeiro passe a lua localização logituginal e latituninal.
Por padrão o planeta que voce estara sera a terra.
coisa que vc pode fazer:
- listar planetas
- verificar se um planeta está apto para ser observado
- receber as istruções para obsevrar o planeta atual momento
- ver que horas o planeta "nasce" e se "poe"
"""


class SkyFieldClient:
  ts: Timescale
  eph: Any
  observaveis: Any

  def __init__(self) -> None:
    self.ts = load.timescale()

    self.eph = api.load(_resolve_data_path("de421.bsp"))
    self.observaveis = {
      "Mercúrio": self.eph["MERCURY BARYCENTER"],
      "Vênus": self.eph["VENUS BARYCENTER"],
      "Marte": self.eph["MARS BARYCENTER"],
      "Júpiter": self.eph["JUPITER BARYCENTER"],
      "Saturno": self.eph["SATURN BARYCENTER"],
      "Urano": self.eph["URANUS BARYCENTER"],
      "Netuno": self.eph["NEPTUNE BARYCENTER"],
      "Lua": self.eph["MOON"],
    }
    self.metadados = {
      "Mercúrio": {"tipo": "planeta", "pai": "Sol"},
      "Vênus": {"tipo": "planeta", "pai": "Sol"},
      "Marte": {"tipo": "planeta", "pai": "Sol"},
      "Júpiter": {"tipo": "planeta", "pai": "Sol"},
      "Saturno": {"tipo": "planeta", "pai": "Sol"},
      "Urano": {"tipo": "planeta", "pai": "Sol"},
      "Netuno": {"tipo": "planeta", "pai": "Sol"},
      "Lua": {"tipo": "satelite", "pai": "Terra"},
    }

  def search_object(
    self,
    objeto: str = "Lua",
    latitude: float = 0,
    longitude: float = 0,
    horario: Time | None = None,
  ):

    alvo = None
    tipo: str = ""

    if objeto in self.observaveis:
      alvo = self.observaveis[objeto]
      tipo = self.metadados[objeto]["tipo"]
    else:
      return SkyFieldClientError(error=2, message="Objeto não encontrado")

    if horario is None:
      horario = self.get_time_now()

    local_observacao = self.eph["Earth"] + wgs84.latlon(latitude * N, longitude * W)
    astrometric = local_observacao.at(horario).observe(alvo)
    alti, azi, dis = astrometric.apparent().altaz()
    vis = alti.degrees > 1.0

    return SearchObjectResponse(
      objeto=ObjectCelest(
        name=objeto, type=tipo, altitude=alti.degrees, azimuth=azi.degrees, visible=vis
      )
    )

  def get_all_observable_objects(
    self,
    latitude: float = 0.0,
    longitude: float = 0.0,
    horario: Time | None = None,
  ) -> AllObjectResponse | SkyFieldClientError:

    local_observacao = self.eph["Earth"] + wgs84.latlon(latitude * N, longitude * W)

    if horario is None:
      horario = self.get_time_now()

    objetos: AllObjectResponse = AllObjectResponse(objects=[])
    planets = self.observaveis
    tipo = self.metadados
    for item in planets:
      astrometric = local_observacao.at(horario).observe(planets[item])
      alti, azi, dis = astrometric.apparent().altaz()
      vis = alti.degrees > 1.0
      objetos.objects.append(
        ObjectCelest(
          name=item,
          visible=vis,
          altitude=alti.degrees,
          azimuth=azi.degrees,
          type=tipo[item]["tipo"],
        )
      )
    return objetos

  def get_observable_objects(self, modo: int = 1):
    if modo == 1:
      return [chaves for chaves in self.observaveis]
    elif modo == 2:
      return self.eph

  def get_time_utc(
    self, ano: int, mes: int, dia: int, hora: int, minuto: int, segundo: int
  ) -> Time:
    return self.ts.utc(
      year=ano, month=mes, day=dia, hour=hora, minute=minuto, second=segundo
    )

  def get_time_now(self) -> Time:
    return self.ts.now()

  def get_moon_phase(self, data: Time) -> MoonDetail:
    sun, moon, earth = self.eph["sun"], self.eph["moon"], self.eph["earth"]

    e = earth.at(data)
    s = e.observe(sun).apparent()
    m = e.observe(moon).apparent()

    _, slon, _ = s.frame_latlon(ecliptic_frame)
    _, mlon, _ = m.frame_latlon(ecliptic_frame)
    phase = (mlon.degrees - slon.degrees) % 360.0

    if phase < 1:
      name = "Lua Nova"
    elif phase < 90:
      name = "Lua Crescente"
    elif phase < 91:  # pequena tolerância para exatamente 90°
      name = "Quarto Crescente"
    elif phase < 180:
      name = "Crescente Gibosa"
    elif phase < 181:  # tolerância para 180°
      name = "Lua Cheia"
    elif phase < 270:
      name = "Minguante Gibosa"
    elif phase < 271:  # tolerância para 270°
      name = "Quarto Minguante"
    else:
      name = "Minguante"
    return MoonDetail(phase=float(phase), phase_name=name)


if __name__ == "__main__":
  # print(load.timescale())
  # print(load.timescale().now())
  # print(datetime.datetime)
  # print(datetime.datetime.now())

  client = SkyFieldClient()
  result2 = client.search_object(
    objeto="Lua", latitude=0, longitude=0, horario=client.get_time_now()
  )
  result = client.get_all_observable_objects(0, 0, load.timescale().now())
  lua = client.get_moon_phase(client.get_time_now())
  print(lua)
  print(result)