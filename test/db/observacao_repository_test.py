import unittest
import sqlite3
from unittest.mock import patch
from datetime import datetime
from src.sky_observer.db.observacao_repository import ObservacaoRepository
from src.sky_observer.db.observacao import Observacao

class ObservacaoRepositoryTest(unittest.TestCase):
    def setUp(self):
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row

        patcher = patch('src.sky_observer.db.observacao_repository.get_connection')
        self.MockConn = patcher.start()
        self.MockConn.return_value = conn
        self.repository = ObservacaoRepository()
        self.addCleanup(patcher.stop)

    def test_insert_and_list(self):
        obs = Observacao(name="Test",
                         latitude=50.0,
                         longitude=100.0,
                         created_at=datetime.now(),
                         updated_at=datetime.now()
                         )
        generated_id = self.repository.insert(obs)

        self.assertEqual(generated_id, 1)

        results = self.repository.list_all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].latitude, 50.0)