import unittest
import sqlite3
from unittest.mock import patch
from datetime import datetime
from sky_observer.db.location_repository import LocationRepository
from sky_observer.db.location import Location

class LocationRepositoryTest(unittest.TestCase):
    def setUp(self):
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row

        patcher = patch('sky_observer.db.location_repository.get_connection')
        self.MockConn = patcher.start()
        self.MockConn.return_value = conn
        self.repository = LocationRepository()
        self.addCleanup(patcher.stop)

    def test_insert_and_list(self):
        loc = Location(name="Test",
                       latitude=50.0,
                       longitude=100.0,
                       created_at=datetime.now(),
                       updated_at=datetime.now()
                       )
        generated_id = self.repository.insert(loc)

        self.assertEqual(generated_id, 1)

        results = self.repository.list_all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].latitude, 50.0)

    def test_update(self):
        loc = Location(
                         id=1,
                         name="Test",
                         latitude=50.0,
                         longitude=100.0,
                         created_at=datetime.now(),
                         updated_at=datetime.now()
                         )
        self.repository.insert(loc)

        loc.name = "Updated"
        loc.latitude = 55.0
        loc.longitude = 100.0
        loc.updated_at = datetime.now()

        rowcount = self.repository.update(loc)
        self.assertEqual(rowcount, 1)

    def test_delete(self):
        loc = Location(
            id=1,
            name="Test",
            latitude=50.0,
            longitude=100.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.repository.insert(loc)
        loc_id = loc.id

        rowcount = self.repository.delete(loc_id)
        self.assertEqual(rowcount, 1)

if __name__ == "__main__":
    unittest.main()