from .observacao import Observacao
from .observacao_repository import ObservacaoRepository
from datetime import datetime

class ObservacaoService:
    def __init__(self):
        self.repo = ObservacaoRepository()

    def register(self, name: str, latitude: float, longitude: float):
        # Caso a observacao tenha uma coordenada invalida
        if not (-90.0 <= latitude <= 90.0) or not (-180.0 <= longitude <= 180.0):
            raise ValueError("Coordenadas inválidas")

        obs = Observacao(
            name=name,
            latitude=latitude,
            longitude=longitude,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Insere os dados e recebe o valor do ultimo id
        generated_id = self.repo.insert(obs)
        return generated_id

    def list(self) -> list[Observacao]:
        return self.repo.list_all()

    def update(self, obs_id: int, name: str, latitude: float, longitude: float):
        # Busca a observação a ser atualizada (original) pelo seu id
        original = self.repo.list_one(obs_id)
        if original is None:
            raise ValueError(f"Observação {obs_id} não encontrada")

        original.name = name
        original.latitude = latitude
        original.longitude = longitude
        original.updated_at = datetime.now()

        return self.repo.update(original)

    def delete(self, obs_id: int):
        deleted_rows = self.repo.delete(obs_id)
        if deleted_rows == 0:
            raise ValueError(f"Observação com id {obs_id} não encontrada.")
        return deleted_rows
