from .connection import get_connection
from .observacao import Observacao

class ObservacaoRepository:
    def __init__(self):
        self.conn = get_connection()
        self._create_table()

    def _create_table(self):
        # Executa a instrução de criar tabela, chamando o cursor implicitamente
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS observacoes (
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
    def insert(self, obs: Observacao) -> int:
        cursor = self.conn.execute(
            "INSERT INTO observacoes (name, latitude, longitude, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (obs.name, obs.latitude, obs.longitude, obs.created_at.isoformat(), obs.updated_at.isoformat())
        )
        self.conn.commit()
        return cursor.lastrowid

    # Lista todos os dados como objetos de Observacao
    def list_all(self) -> list[Observacao]:
        rows = self.conn.execute("SELECT * FROM observacoes ORDER BY created_at DESC").fetchall()
        return [self._row_to_obs(row) for row in rows]

    def list_one(self, obs_id: int) -> Observacao:
        cursor = self.conn.execute("""
            SELECT * FROM observacoes WHERE id = ?
        """, (obs_id,))
        row = cursor.fetchone()
        return self._row_to_obs(row)

    # Transforma os dados como objetos de Observacao ao invés de rows brutas de SQL (Data Mapper)
    def _row_to_obs(self, row) -> Observacao:
        from datetime import datetime
        return Observacao(
            id=row["id"],
            name=row["name"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    # Incompleto...
    def update(self, obs: Observacao) -> int:
        cursor = self.conn.execute("""
            UPDATE observacoes
            SET name = ?, latitude = ?, longitude = ?, updated_at = ?
            WHERE id = ?
        """, (obs.name, obs.latitude, obs.longitude, obs.updated_at.isoformat(), obs.id))
        self.conn.commit()
        return cursor.rowcount

    # Deleta um atributo por id
    def delete(self, obs_id: int) -> int:
        cursor = self.conn.execute("""
            DELETE FROM observacoes WHERE id = ?
        """, (obs_id,))
        self.conn.commit()
        return cursor.rowcount