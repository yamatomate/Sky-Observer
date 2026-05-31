from dataclasses import dataclass

from skyfield import api, units
from skyfield.api import N, W, load, wgs84


@dataclass(frozen=True)
class ObjetoVisivelResponse:
  visible: bool
  altitude: float
  azimuth: float

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
  def __init__(self, latitude: float, longitude: float):
    """Classe que simplfica a busca dos objetos no ceu. Use a função objetos_observaveis para saber todos os objetos observaveis disponivveis para calculo.\n
    posicao (tupla): recebe dois valores a latitude e a logitude\nexemplo: (5.3444, 2.5555)"""
    self.posicao_atual: tuple[float, float] = (latitude,longitude)
    self.escala_tempo = load.timescale()

    EPH = api.load("de421.bsp")
    self.EPH = EPH

    self.TERRA = EPH["Earth"]
    planetas = {
      "Mercúrio": EPH["Mercury"],
      "Vênus": EPH["Venus"],
      "Terra": EPH["Earth"],
      "Marte": EPH["Mars"],
      "Júpiter": EPH[5],
      "Saturno": EPH[6],
      "Urano": EPH[7],
      "Netuno": EPH[8],
    }
    self.planetas = planetas
    self.satelites = {"Lua": EPH["Moon"]}
    self.extra = {"Plutão": EPH[9]}

    self.observaveis = self.planetas | self.satelites | self.extra

  def search_object(
    self,
    objeto="Moon",
    latitude: float = None,
    longitude: float = None,
    horario=load.timescale().now(),
  ):
    """Verificar se no na hora passada se o objeto está visivel no ceu da terra.\n
    objeto: nome do objeto a ser observado\n
    localizacao = (latitude, logitude): tupla que possui logitude e latitude\n
    horario: por padrão será usado o atual"""

    alvo = None
    if latitude is None and longitude is None:
      latitude = self.posicao_atual[0]
      longitude = self.posicao_atual[1]

    if objeto in self.observaveis:
      alvo = self.observaveis[objeto]
    elif objeto in self.EPH and objeto != 0:
      alvo = self.EPH[objeto]
    else:
      # alvo não foi nem encotrado na lista de observaveis e nem na EPH
      return None

    local_observacao = self.TERRA + wgs84.latlon(latitude * N, longitude * W)
    astrometric = local_observacao.at(horario).observe(alvo)
    alt, az, d = astrometric.apparent().altaz()
    vis = alt.degrees > units.Angle(degrees=1).degrees
    return ObjetoVisivelResponse(vis, alt, az)

  def observable_objects(self, modo: int = 1):
    if modo == 1:
      return [chaves for chaves in self.observaveis]
    elif modo == 2:
      return self.EPH
