# pyright: reportPrivateUsage=false
from unittest.mock import MagicMock, patch

import pytest

from sky_observer.infra.skyfield.client import (
  AllObjectResponse,
  MoonDetail,
  SkyFieldClient,
  SkyFieldClientError,
)


@patch("sky_observer.infra.skyfield.client.load.timescale")
@patch("sky_observer.infra.skyfield.client.api.load")
def test_skyfield_client_init(mock_load: MagicMock, mock_timescale: MagicMock):
  # Arrange
  mock_eph = MagicMock()
  mock_load.return_value = mock_eph

  # Act
  client = SkyFieldClient()

  # Assert
  mock_load.assert_called_once_with("de421.bsp")
  mock_timescale.assert_called_once()
  assert "Mercúrio" in client.observaveis
  assert "Lua" in client.observaveis


@patch("sky_observer.infra.skyfield.client.load.timescale")
@patch("sky_observer.infra.skyfield.client.api.load")
@patch("sky_observer.infra.skyfield.client.wgs84.latlon")
def test_search_object_success(
  mock_latlon: MagicMock, mock_load: MagicMock, mock_timescale: MagicMock
):
  # Arrange
  mock_eph = MagicMock()
  mock_load.return_value = mock_eph
  client = SkyFieldClient()

  mock_earth = MagicMock()
  mock_eph.__getitem__.return_value = mock_earth

  mock_local = MagicMock()
  mock_earth.__add__.return_value = mock_local

  mock_astrometric = MagicMock()
  mock_local.at.return_value.observe.return_value = mock_astrometric

  mock_alt = MagicMock()
  mock_alt.degrees = 45.0
  mock_az = MagicMock()
  mock_az.degrees = 120.0
  mock_astrometric.apparent.return_value.altaz.return_value = (
    mock_alt,
    mock_az,
    MagicMock(),
  )

  # Act
  res = client.search_object(objeto="Lua", latitude=-23.0, longitude=-46.0)

  # Assert
  assert not isinstance(res, SkyFieldClientError)
  assert res.objeto.name == "Lua"
  assert res.objeto.type == "satelite"
  assert res.objeto.visible is True
  assert res.objeto.altitude == 45.0
  assert res.objeto.azimuth == 120.0


@patch("sky_observer.infra.skyfield.client.load.timescale")
@patch("sky_observer.infra.skyfield.client.api.load")
def test_search_object_not_found(mock_load: MagicMock, mock_timescale: MagicMock):
  # Arrange
  mock_load.return_value = MagicMock()
  client = SkyFieldClient()

  # Act
  res = client.search_object(objeto="NonExistent")

  # Assert
  assert isinstance(res, SkyFieldClientError)
  assert res.error == 2
  assert "Objeto não encontrado" in res.message


@patch("sky_observer.infra.skyfield.client.load.timescale")
@patch("sky_observer.infra.skyfield.client.api.load")
@patch("sky_observer.infra.skyfield.client.wgs84.latlon")
def test_get_all_observable_objects(
  mock_latlon: MagicMock, mock_load: MagicMock, mock_timescale: MagicMock
):
  # Arrange
  mock_eph = MagicMock()
  mock_load.return_value = mock_eph
  client = SkyFieldClient()

  mock_earth = MagicMock()
  mock_eph.__getitem__.return_value = mock_earth

  mock_local = MagicMock()
  mock_earth.__add__.return_value = mock_local

  mock_astrometric = MagicMock()
  mock_local.at.return_value.observe.return_value = mock_astrometric

  mock_alt = MagicMock()
  mock_alt.degrees = 10.0
  mock_az = MagicMock()
  mock_az.degrees = 90.0
  mock_astrometric.apparent.return_value.altaz.return_value = (
    mock_alt,
    mock_az,
    MagicMock(),
  )

  # Act
  res = client.get_all_observable_objects(latitude=-23.0, longitude=-46.0)

  # Assert
  assert isinstance(res, AllObjectResponse)
  assert len(res.objects) == len(client.observaveis)
  assert res.objects[0].altitude == 10.0
  assert res.objects[0].azimuth == 90.0


@pytest.mark.parametrize(
  "phase_deg, expected_name",
  [
    (0.5, "Lua Nova"),
    (45.0, "Lua Crescente"),
    (90.5, "Quarto Crescente"),
    (140.0, "Crescente Gibosa"),
    (180.5, "Lua Cheia"),
    (220.0, "Minguante Gibosa"),
    (270.5, "Quarto Minguante"),
    (310.0, "Minguante"),
  ],
)
@patch("sky_observer.infra.skyfield.client.load.timescale")
@patch("sky_observer.infra.skyfield.client.api.load")
@patch("sky_observer.infra.skyfield.client.ecliptic_frame")
def test_get_moon_phase(
  _mock_ecliptic_frame: MagicMock,
  mock_load: MagicMock,
  mock_timescale: MagicMock,
  phase_deg: float,
  expected_name: str,
):
  # Arrange
  mock_eph = MagicMock()
  mock_load.return_value = mock_eph
  client = SkyFieldClient()

  mock_earth = MagicMock()
  mock_eph.__getitem__.return_value = mock_earth

  mock_e_at = MagicMock()
  mock_earth.at.return_value = mock_e_at

  mock_s_observed = MagicMock()
  mock_m_observed = MagicMock()
  mock_e_at.observe.side_effect = [mock_s_observed, mock_m_observed]

  mock_s_apparent = MagicMock()
  mock_m_apparent = MagicMock()
  mock_s_observed.apparent.return_value = mock_s_apparent
  mock_m_observed.apparent.return_value = mock_m_apparent

  mock_slon = MagicMock()
  mock_slon.degrees = 0.0
  mock_mlon = MagicMock()
  mock_mlon.degrees = phase_deg

  mock_s_apparent.frame_latlon.return_value = (None, mock_slon, None)
  mock_m_apparent.frame_latlon.return_value = (None, mock_mlon, None)

  mock_time = MagicMock()

  # Act
  res = client.get_moon_phase(mock_time)

  # Assert
  assert isinstance(res, MoonDetail)
  assert res.phase == phase_deg
  assert res.phase_name == expected_name


@patch("sky_observer.infra.skyfield.client.load.timescale")
@patch("sky_observer.infra.skyfield.client.api.load")
def test_get_time_methods(mock_load: MagicMock, mock_timescale: MagicMock):
  # Arrange
  mock_ts = MagicMock()
  mock_timescale.return_value = mock_ts
  client = SkyFieldClient()

  # Act & Assert
  client.get_time_now()
  mock_ts.now.assert_called_once()

  client.get_time_utc(2026, 6, 1, 12, 0, 0)
  mock_ts.utc.assert_called_once_with(
    year=2026, month=6, day=1, hour=12, minute=0, second=0
  )
