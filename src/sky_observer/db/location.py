from dataclasses import dataclass
from datetime import datetime

# Entidade que representa a tabela location no SQLite
@dataclass
class Location:
    name: str
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime
    id: int | None = None