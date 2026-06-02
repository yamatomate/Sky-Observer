from dataclasses import dataclass
from skyfield import api, units
from skyfield.api import N, W, Angle, load, wgs84

@dataclass(frozen=True)
class SearchObjectResponse:
  visible: bool
  altitude: Angle
  azimuth: Angle

@dataclass(frozen=True)
class AllObjectResponse:
  name: str
  visible: bool
  altitude: Angle
  azimuth: Angle


@dataclass(frozen=True)
class SearchObjectError:
  error: int
  message: str

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
  posicao_atual : tuple[float, float]
  escala_tempo : api.Timescale

  def __init__(self, with_earth=False) -> None:
    self.escala_tempo = load.timescale()

    EPH = api.load("de421.bsp")
    self._EPH = EPH

    self.TERRA = EPH["Earth"]

    if with_earth:
      self.planetas = {
        "Mercúrio": EPH["Mercury"],
        "Vênus": EPH["Venus"],
        "Terra": EPH["Earth"],
        "Marte": EPH["Mars"],
        "Júpiter": EPH[5],
        "Saturno": EPH[6],
        "Urano": EPH[7],
        "Netuno": EPH[8],
      }
    else:
      self.planetas = {
        "Mercúrio": EPH["Mercury"],
        "Vênus": EPH["Venus"],
        "Marte": EPH["Mars"],
        "Júpiter": EPH[5],
        "Saturno": EPH[6],
        "Urano": EPH[7],
        "Netuno": EPH[8],
      }
    
    self.satelites = {"Lua": EPH["Moon"]}
    self.extra = {"Plutão": EPH[9]}
    self.observaveis = self.planetas | self.satelites | self.extra

  def set_location(self, latitude: float = 0.0, logitude: float = 0.0):
    self.posicao_atual = (latitude, logitude)

  def search_object(
    self,
    objeto="Moon",
    horario=load.timescale().now(),
  ):
    """Verificar se no na hora passada se o objeto está visivel no ceu da terra.\n
    objeto: nome do objeto a ser observado\n
    localizacao = (latitude, logitude): tupla que possui logitude e latitude\n
    horario: por padrão será usado o atual"""

    alvo = None

    if objeto in self.observaveis:
      alvo = self.observaveis[objeto]
    elif objeto in self._EPH and objeto != 0:
      alvo = self._EPH[objeto]
    elif self.posicao_atual == None:
      # alvo não foi nem encotrado na lista de observaveis e nem na EPH
      return SearchObjectError(error=1, message="Posicao atual não definida")
    else:
      return SearchObjectError(error=2, message="Objeto não encontrado")

    latitude = self.posicao_atual[0]
    longitude = self.posicao_atual[1]

    local_observacao = self.TERRA + wgs84.latlon(latitude * N, longitude * W)
    astrometric = local_observacao.at(horario).observe(alvo)
    alti, azi, dis = astrometric.apparent().altaz()
    vis = alti.degrees > units.Angle(degrees=1).degrees

    return SearchObjectResponse(visible=vis, altitude=alti, azimuth=azi)

  def list_all_observable_objects(self, horario : load.timescale = load.timescale().now()):
    if self.posicao_atual == None:
      # alvo não foi nem encotrado na lista de observaveis e nem na EPH
      return SearchObjectError(error=1, message="Posicao atual não definida")

    latitude = self.posicao_atual[0]
    longitude = self.posicao_atual[1]

    local_observacao = self.TERRA + wgs84.latlon(latitude * N, longitude * W)

    objetos = []
    for key, value in self.observaveis.items():
      print(key)
      astrometric = local_observacao.at(horario).observe(value)
      alti, azi, dis = astrometric.apparent().altaz()
      vis = alti.degrees > units.Angle(degrees=1).degrees
      objetos.append(AllObjectResponse(name=key,visible=vis, altitude=alti, azimuth=azi))

    print(objetos)

  def observable_objects(self, modo: int = 1):
    if modo == 1:
      return [chaves for chaves in self.observaveis]
    elif modo == 2:
      return self._EPH

if __name__ == "__main__":
  client = SkyFieldClient()
  client.set_location(latitude=0,logitude=0)
  print(client.search_object(objeto="Moon"))
  print(client.list_all_observable_objects())
