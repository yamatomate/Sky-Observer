from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class PlanetVisibility:
  name: str
  detail: str  # "Alt. 62° / Az. 188°"
  status: Literal["green", "yellow", "red"]


@dataclass(frozen=True)
class SkyMetrics:
  cloud_cover: str
  seeing: str
  humidity: str
  moon_phase: str


@dataclass(frozen=True)
class ConditionsResult:
  location: str
  score: int
  status: Literal["good", "fair", "bad"]
  title: str
  subtitle: str
  metrics: SkyMetrics
  planets: list[PlanetVisibility]
  is_object_context: bool = False


@dataclass(frozen=True)
class CelestialObject:
  icon: str
  name: str
  type: str
  details: str


@dataclass(frozen=True)
class CityResult:
  name: str
  latitude: float
  longitude: float
  country: str