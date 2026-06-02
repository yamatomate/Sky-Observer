# db — Camada de Acesso a Dados e Persistência

Módulo responsável por gerenciar a conexão e persistência de dados utilizando o banco de dados **SQLite**. A principal funcionalidade deste módulo é o CRUD para gerenciar a lista de **localizações favoritas** do usuário.

## Estrutura

```bash
db/
├── connection.py            # Singleton para conexão com o banco SQLite
├── location.py              # Entidade / Dataclass representante da tabela
├── location_repository.py   # Data Mapper para execução de comandos SQL brutas
├── location_service.py      # Regras de negócio e validações das localizações
└── README.md
```

## Componentes

### 1. Conexão (`connection.py`)

Gerencia a conexão única (**Singleton**) com o banco de dados SQLite (`app.db`).

- **`get_connection(db_path="app.db") -> sqlite3.Connection`**:
  - Retorna a conexão global ativa ou cria uma nova conexão.
  - Configura `check_same_thread=False` para permitir o acesso multi-threaded (necessário para rodar chamadas em background threads na UI).
  - Define `row_factory = sqlite3.Row` permitindo acessar colunas do resultado SQL por nome (semelhante a um dicionário Python).

---

### 2. Entidade de Dados (`location.py`)

Dataclass imutável que mapeia as colunas da tabela `locations` no SQLite para a linguagem orientada a objetos.

| Campo        | Tipo          | Descrição                                                                             |
| ------------ | ------------- | ------------------------------------------------------------------------------------- |
| `name`       | `str`         | Nome da cidade/localização                                                            |
| `latitude`   | `float`       | Latitude em graus decimais                                                            |
| `longitude`  | `float`       | Longitude em graus decimais                                                           |
| `created_at` | `datetime`    | Data e hora de criação do favorito                                                    |
| `updated_at` | `datetime`    | Data e hora da última atualização                                                     |
| `id`         | `int \| None` | Chave primária autoincrementada (inicia como `None` antes de ser persistido no banco) |

---

### 3. Repositório (`location_repository.py`)

Camada responsável por fazer a ponte entre as entidades em código e o banco de dados SQL (Data Mapper). Ela se encarrega de:

- **Auto-Inicialização**: No construtor (`__init__`), cria a tabela `locations` automaticamente caso ela não exista.
- **`insert(loc: Location) -> int`**: Insere uma nova linha e retorna o ID gerado pelo banco de dados.
- **`list_all() -> list[Location]`**: Lista todos os locais ordenados de forma decrescente pela data de criação.
- **`list_one(loc_id: int) -> Location`**: Busca um local específico pelo ID.
- **`update(loc: Location) -> int`**: Atualiza nome, coordenadas e data de modificação, retornando o número de linhas afetadas.
- **`delete(loc_id: int) -> int`**: Remove um local pelo ID, retornando o número de linhas afetadas.

---

### 4. Serviço (`location_service.py`)

Camada que implementa as regras de negócio e validações antes de enviar os dados para persistência:

- **Validação Geográfica**:
  - Ao registrar, verifica se as coordenadas são válidas:
    - $-90.0 \leq \text{latitude} \leq 90.0$
    - $-180.0 \leq \text{longitude} \leq 180.0$
    - Lança um `ValueError("Coordenadas inválidas")` se as restrições forem violadas.
- **Orquestração**:
  - Preenche os timestamps (`created_at` e `updated_at`) com a data/hora atual automaticamente no registro e atualização.
  - Valida a existência do favorito no banco antes de disparar atualizações e deleções, lançando exceções se o ID não for encontrado.

---

## Uso

```python
from sky_observer.db.location_service import LocationService

service = LocationService()

# 1. Registrar um favorito (com validações geográficas inclusas)
try:
    generated_id = service.register(
        name="Curitiba, PR",
        latitude=-25.4284,
        longitude=-49.2733
    )
    print(f"Local salvo com ID: {generated_id}")
except ValueError as e:
    print(f"Erro de validação: {e}")

# 2. Listar favoritos salvos
favoritos = service.list()
for fav in favoritos:
    print(f"{fav.id}: {fav.name} ({fav.latitude}, {fav.longitude})")

# 3. Atualizar dados
service.update(loc_id=1, name="Curitiba Central", latitude=-25.4284, longitude=-49.2733)

# 4. Deletar favorito
service.delete(loc_id=1)
```

---

## Testes

A camada de banco de dados conta com testes unitários rodando em bancos de dados em memória (`sqlite3.connect(':memory:')`), isolando completamente os testes do arquivo de banco de dados físico de produção (`app.db`).

- **`location_repository_test.py`**: Valida a integridade das queries SQL (`insert`, `list_all`, `update` e `delete`).
- **`location_service_test.py`**: Valida as regras de negócio de coordenadas válidas/inválidas e o fluxo de chamadas do repositório mockado.

Para rodar a suíte de testes de banco de dados:

```bash
uv run pytest test/db/ -v
```
