from observacao import Observacao
from observacao_repository import ObservacaoRepository
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