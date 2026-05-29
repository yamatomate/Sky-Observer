# openmeteo — Cliente para Open-Meteo API

Módulo de infraestrutura responsável por consultar dados meteorológicos e de geolocalização
através da [Open-Meteo API](https://open-meteo.com/).

## Estrutura

```
openmeteo/
├── client.py    # Cliente HTTP com cache e retry
├── utils.py     # Mapa de códigos WMO para descrições em português
└── README.md
```

## Componentes

### `OpenMeteoClient` (`client.py`)

Cliente que integra duas APIs públicas da Open-Meteo:

| Método | API | Retorno | Falha |
|---|---|---|---|
| `get_weather(lat, lon)` | `/v1/forecast` | `WeatherDataResponse \| None` | `None` se a requisição falhar ou a resposta vier incompleta |
| `search_location(name)` | `/v1/search` (Geocoding) | `LocationResponse \| None` | `None` se a requisição falhar ou nenhum resultado for encontrado |

**Características:**
- Cache local de 5 minutos (`niquests_cache`) para reduzir chamadas repetidas
- Retry automático (3 tentativas com backoff) em erros 5xx
- Tratamento de falhas via logging (não propaga exceções para o caller)

### `WeatherDataResponse` (`client.py`)

Dataclass imutável com os campos retornados por `get_weather`:

| Campo | Tipo | Descrição |
|---|---|---|
| `temperature_c` | `float` | Temperatura em °C |
| `humidity_pct` | `float` | Umidade relativa (%) |
| `cloud_cover_pct` | `float` | Cobertura de nuvens (%) |
| `precipitation_mm` | `float` | Precipitação em mm |
| `weather_code` | `int` | Código WMO bruto |
| `weather_description` | `str` | Código WMO traduzido (ex.: "Céu limpo") |
| `wind_speed_kmh` | `float` | Velocidade do vento em km/h |
| `visibility_m` | `float` | Visibilidade em metros |
| `is_day` | `bool` | `True` se for dia, `False` se for noite |

### `LocationResponse` (`client.py`)

Dataclass imutável com os campos retornados por `search_location`:

| Campo | Tipo | Descrição |
|---|---|---|
| `name` | `str` | Nome da localidade buscada |
| `latitude` | `float` | Latitude em graus decimais |
| `longitude` | `float` | Longitude em graus decimais |
| `elevation` | `float` | Elevação em metros |
| `country` | `str` | Nome do país |
| `country_code` | `str` | Código ISO do país (ex.: "BR") |
| `timezone` | `str` | Fuso horário IANA (ex.: "America/Sao_Paulo") |
| `population` | `int` | População da localidade |

### `WMO_CODES` (`utils.py`)

Dicionário que traduz códigos WMO (Organização Meteorológica Mundial) para
descrições legíveis em português brasileiro — de `0` ("Céu limpo") a `99`
("Tempestade c/ granizo forte").

## Uso

```python
from sky_observer.infra.openmeteo.client import OpenMeteoClient

client = OpenMeteoClient()

# Clima atual
weather = client.get_weather(-23.5505, -46.6333)
if weather:
    print(weather.temperature_c, weather.weather_description)

# Busca de localidade
loc = client.search_location("São Paulo")
if loc:
    print(loc.latitude, loc.longitude, loc.timezone)
```

## Dependências

- `openmeteo-requests` — SDK oficial da Open-Meteo
- `niquests` — HTTP client alternativo ao `requests`
- `niquests-cache` — Cache HTTP com suporte a TTL
- `urllib3` — Configuração de retry

## Testes

O módulo possui testes unitários que cobrem os cenários de sucesso de
`get_weather` e `search_location`, mockando as chamadas HTTP externas via
`unittest.mock.patch`. Não há testes para cenários de falha (retorno `None`)
no momento.

### `test_weather_data_response_success`

Mocka a resposta da API `/v1/forecast` com 8 variáveis climáticas e verifica
se o `WeatherDataResponse` retornado contém os valores esperados — incluindo
a tradução do código WMO (`1 → "Predom. claro"`).

### `test_search_location_success`

Mocka a resposta da API Geocoding com dados da cidade de Teresina e verifica
se o `LocationResponse` retornado contém os campos corretos (coordenadas,
país, fuso horário, população).

```bash
pytest test/ -k "openmeteo" -v
```
