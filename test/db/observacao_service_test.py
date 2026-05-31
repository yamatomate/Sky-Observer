import unittest
from unittest.mock import MagicMock, patch
from sky_observer.db.observacao_service import ObservacaoService

class ObservacaoServiceTest(unittest.TestCase):
    def setUp(self):
        patcher = patch("sky_observer.db.observacao_service.ObservacaoRepository")
        self.MockRepo = patcher.start()
        self.mock_repo = MagicMock()
        self.MockRepo.return_value = self.mock_repo
        self.service = ObservacaoService()
        self.addCleanup(patcher.stop)

    def test_registrar_coordenadas_validas(self):
        self.mock_repo.insert.return_value = 1

        id_gerado = self.service.register(name="Teste", latitude=-5.08, longitude=-42.8)

        self.assertEqual(id_gerado, 1)
        self.mock_repo.insert.assert_called_once()

    def test_register_invalid_latitude(self):
        with self.assertRaises(ValueError):
            self.service.register(name="Teste", latitude=999, longitude=-42.8)

    def test_register_invalid_longitude(self):
        with self.assertRaises(ValueError):
            self.service.register(name="Teste", latitude=-5.08, longitude=999)

    def test_update(self):
        self.mock_repo.update.return_value = 1
        rows = self.service.update(obs_id=1, name="Test", latitude=55.0, longitude=55.0)
        self.assertGreaterEqual(1, rows)

    def test_delete(self):
        self.mock_repo.delete.return_value = 1
        rows = self.service.delete(obs_id=1)
        self.assertGreaterEqual(1, rows)

if __name__ == "__main__":
    unittest.main()