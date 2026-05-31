from .location import Location
from .location_repository import LocationRepository
from datetime import datetime

class LocationService:
    def __init__(self):
        self.repo = LocationRepository()

    def register(self, name: str, latitude: float, longitude: float):
        # Caso a localização tenha uma coordenada invalida
        if not (-90.0 <= latitude <= 90.0) or not (-180.0 <= longitude <= 180.0):
            raise ValueError("Coordenadas inválidas")

        loc = Location(
            name=name,
            latitude=latitude,
            longitude=longitude,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Insere os dados e recebe o valor do ultimo id
        generated_id = self.repo.insert(loc)
        return generated_id

    def list(self) -> list[Location]:
        return self.repo.list_all()

    def update(self, loc_id: int, name: str, latitude: float, longitude: float):
        # Busca a localização a ser atualizada (original) pelo seu id
        original = self.repo.list_one(loc_id)
        if original is None:
            raise ValueError(f"Localização {loc_id} não encontrada")

        original.name = name
        original.latitude = latitude
        original.longitude = longitude
        original.updated_at = datetime.now()

        return self.repo.update(original)

    def delete(self, loc_id: int):
        deleted_rows = self.repo.delete(loc_id)
        if deleted_rows == 0:
            raise ValueError(f"Localização com id {loc_id} não encontrada.")
        return deleted_rows
