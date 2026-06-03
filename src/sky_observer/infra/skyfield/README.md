# skyfield — Cliente para Efemérides Astronômicas

Módulo de infraestrutura responsável por consultar posições e visibilidade de corpos celestes utilizando a biblioteca [Skyfield](https://rhodesmill.org/skyfield/) e os arquivos de efemérides DE421 da NASA/JPL.

## Estrutura

```
skyfield/
├── client.py    # Cliente para cálculos astronômicos
└── README.md
```

## Componentes

### `SkyFieldClient` (`client.py`)

Cliente stateless que calcula posições astronômicas e visibilidade de objetos no céu, baseado em uma localização geográfica e horário.

**Características:**
- Carrega arquivo de efemérides `de421.bsp` (uma única vez no construtor)
- Construtor sem parâmetros obrigatórios (stateless para injeção de dependência)
- Requer definição de localização via `set_location()` antes dos cálculos
- Tratamento de erros com retorno de `SearchObjectError` quando localização não definida ou objeto não encontrado

### Métodos

| Método | Descrição | Retorno |
|---|---|---|
| `set_location(latitude, longitude)` | Define a posição do observador na Terra | `None` |
| `search_object(objeto, horario)` | Verifica se um objeto está visível no céu no horário especificado | `SearchObjectResponse` ou `SearchObjectError` |
| `list_all_observable_objects(horario)` | Lista todos os objetos observáveis com suas posições | `list[AllObjectResponse]` ou `SearchObjectError` |
| `observable_objects(modo)` | Retorna lista de nomes dos objetos disponíveis | `list[str]` |

### `SearchObjectResponse` (`client.py`)

Dataclass imutável retornada por `search_object` em caso de sucesso:

| Campo | Tipo | Descrição |
|---|---|---|
| `visible` | `bool` | `True` se o objeto está acima do horizonte (> 1° de altitude) |
| `altitude` | `Angle` | Ângulo de altitude do objeto (graus) |
| `azimuth` | `Angle` | Ângulo de azimute do objeto (graus) |

### `AllObjectResponse` (`client.py`)

Dataclass imutável retornada por `list_all_observable_objects`:

| Campo | Tipo | Descrição |
|---|---|---|
| `name` | `str` | Nome do objeto em português |
| `visible` | `bool` | Indica se o objeto está visível |
| `altitude` | `Angle` | Ângulo de altitude |
| `azimuth` | `Angle` | Ângulo de azimute |

### `SearchObjectError` (`client.py`)

Dataclass retornada em caso de erro:

| Campo | Tipo | Descrição |
|---|---|---|
| `error` | `int` | Código do erro (`1` = localização não definida, `2` = objeto não encontrado) |
| `message` | `str` | Mensagem descritiva do erro |

### Objetos Observáveis

O cliente inclui os seguintes objetos:

| Categoria | Objetos |
|---|---|
| **Planetas** | Mercúrio, Vênus, Marte, Júpiter, Saturno, Urano, Netuno |
| **Satélites** | Lua |
| **Extras** | Plutão |

## Uso

```python
from sky_observer.infra.skyfield.client import SkyFieldClient

# Inicializa cliente (stateless, sem parâmetros obrigatórios)
client = SkyFieldClient()

# Define localização (Teresina, PI)
client.set_location(latitude=-5.0892, longitude=-42.8019)

# Verifica visibilidade de Marte agora
resultado = client.search_object("Marte")
if hasattr(resultado, 'visible'):
    print(f"Marte visível: {resultado.visible}")
    print(f"Altitude: {resultado.altitude.degrees:.1f}°")
    print(f"Azimute: {resultado.azimuth.degrees:.1f}°")
else:
    print(f"Erro {resultado.error}: {resultado.message}")

# Lista todos os objetos observáveis
objetos = client.list_all_observable_objects()
for obj in objetos:
    status = "✅ Visível" if obj.visible else "❌ Não visível"
    print(f"{obj.name}: {status} (Alt: {obj.altitude.degrees:.0f}°)")

# Obtém apenas os nomes dos objetos
nomes = client.observable_objects(modo=1)
print(f"Objetos disponíveis: {nomes}")
```

## Dependências

- `skyfield` — Cálculos astronômicos e efemérides
- `de421.bsp` — Arquivo de efemérides da NASA/JPL (baixado automaticamente na primeira execução)

## Notas de Implementação

### Stateless
O cliente segue o princípio **stateless**:
- Construtor sem parâmetros obrigatórios
- Estado de localização é definido via método `set_location()`
- Arquivo de efemérides é carregado uma única vez na inicialização

### Validações
- Retorna `SearchObjectError` com código `1` se `set_location()` não foi chamado
- Retorna `SearchObjectError` com código `2` se o objeto não for encontrado
- Considera um objeto **visível** quando altitude > 1°

### Formatação para View
**Importante:** Este cliente retorna dados brutos (`Angle`, `bool`). A formatação para o dicionário exigido pela view (com strings como `"Alt. 45° · Az. 120°"`) deve ser feita na **camada de serviço**, não neste cliente.

## Testes

```bash
pytest test/ -k "skyfield" -v
```