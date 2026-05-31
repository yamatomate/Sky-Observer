from .connection import get_connection
from .location import Location

class LocationRepository:
    def __init__(self):
        self.conn = get_connection()
        self._create_table()

    def _create_table(self):
        # Executa a instrução de criar tabela, chamando o cursor implicitamente
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    # Insere dados na tabela e retorna o id da ultima linha inserida
    def insert(self, loc: Location) -> int:
        cursor = self.conn.execute(
            "INSERT INTO locations (name, latitude, longitude, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (loc.name, loc.latitude, loc.longitude, loc.created_at.isoformat(), loc.updated_at.isoformat())
        )
        self.conn.commit()
        return cursor.lastrowid

    # Lista todos os dados como objetos de Location
    def list_all(self) -> list[Location]:
        rows = self.conn.execute("SELECT * FROM locations ORDER BY created_at DESC").fetchall()
        return [self._row_to_loc(row) for row in rows]

    def list_one(self, loc_id: int) -> Location:
        cursor = self.conn.execute("""
            SELECT * FROM locations WHERE id = ?
        """, (loc_id,))
        row = cursor.fetchone()
        return self._row_to_loc(row)

    # Transforma os dados como objetos de Location ao invés de rows brutas de SQL (Data Mapper)
    def _row_to_loc(self, row) -> Location:
        from datetime import datetime
        return Location(
            id=row["id"],
            name=row["name"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    # Incompleto...
    def update(self, loc: Location) -> int:
        cursor = self.conn.execute("""
            UPDATE locations
            SET name = ?, latitude = ?, longitude = ?, updated_at = ?
            WHERE id = ?
        """, (loc.name, loc.latitude, loc.longitude, loc.updated_at.isoformat(), loc.id))
        self.conn.commit()
        return cursor.rowcount

    # Deleta um atributo por id
    def delete(self, loc_id: int) -> int:
        cursor = self.conn.execute("""
            DELETE FROM locations WHERE id = ?
        """, (loc_id,))
        self.conn.commit()
        return cursor.rowcount