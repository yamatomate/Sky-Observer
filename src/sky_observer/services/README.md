# services — Camada de Negócio e Serviços

Módulo central do domínio do **Sky Observer**, responsável por orquestrar os dados meteorológicos (da camada `infra/openmeteo`), os cálculos astronômicos (da camada `infra/skyfield`) e as regras de banco de dados (da camada `db`) para entregar modelos de dados unificados e prontos para a interface gráfica (UI).

## Estrutura

```bash
services/
├── models.py                # Dataclasses de retorno unificadas para a UI
├── observation_service.py   # Lógica de negócio, score e orquestração de dados
└── README.md
```

## Componentes

### `ObservationService` (`observation_service.py`)

A classe de serviço central que cruza dados externos e executa fórmulas de pontuação astronômica:

| Método                                          | Finalidade                                                                         | Retorno                          | Dependências                        |
| ----------------------------------------------- | ---------------------------------------------------------------------------------- | -------------------------------- | ----------------------------------- |
| `get_conditions(lat, lon, name)`                | Retorna condições do céu, score, métricas e visibilidade dos planetas              | `ConditionsResult`               | `OpenMeteoClient`, `SkyFieldClient` |
| `get_visible_objects(lat, lon, horario)`        | Lista os objetos celestes (planetas e Lua) e suas posições (Alt/Az) para o momento | `list[CelestialObject]`          | `SkyFieldClient`                    |
| `search_location(query)`                        | Busca uma localidade geográfica intermediando com o geocoder                       | `CityResult \| None`             | `OpenMeteoClient`                   |
| `_calculate_score(cloud, humidity, visibility)` | Gera a pontuação de qualidade do céu de 0 a 100                                    | `float`                          | Nenhuma (Algoritmo interno)         |
| `_score_to_status(score)`                       | Classifica a pontuação nos termos da UI (`"good"`, `"fair"`, `"bad"`)              | `Literal["good", "fair", "bad"]` | Nenhuma                             |

#### Fórmulas de Domínio Internas

- **Score Astronômico**: Calculado a partir de uma média ponderada com pesos:
  - **Nuvens (60%)**: Decaimento linear (0% nuvens = 60 pts; 100% nuvens = 0 pts).
  - **Umidade (15%)**: 15 pts se umidade < 60%. Acima de 60%, sofre redução linear de 2.5% por cada 1% excedente.
  - **Visibilidade (25%)**: Escala de 0 a 10 km (10.000m). Acima de 10 km, pontuação máxima (25 pts).
- **Escala de Seeing**: Interpolado dinamicamente em uma escala de 1 a 8 baseada na pontuação final do céu.
- **Fase/Iluminação Lunar**: Conversão trigonométrica do ângulo da fase da lua ($0^\circ$ a $360^\circ$) para a porcentagem de iluminação real de $0\%$ a $100\%$ ($50 \times (1 - \cos(\text{phase}))\%$).

---

### Dataclasses de Retorno (`models.py`)

Dataclasses que formam o contrato estrito de dados entre o Back-end e a UI:

#### `ConditionsResult`

Representa o estado geral de observação de uma localidade.

- `location`: Nome da localidade (`str`).
- `score`: Pontuação final de observação de 0 a 100 (`int`).
- `status`: Indicador visual: `"good"`, `"fair"` ou `"bad"`.
- `title` / `subtitle`: Títulos descritivos legíveis (ex: "Céu Excelente").
- `metrics`: Instância de `SkyMetrics`.
- `planets`: Lista de `PlanetVisibility`.
- `is_object_context`: Contexto da view (se está olhando um objeto em detalhe).

#### `SkyMetrics`

Métricas climatológicas e astronômicas básicas para os cartões de dados da UI.

- `cloud_cover`: Porcentagem de nuvens formatada (`str`).
- `seeing`: Nota do seeing de 1 a 8 (`str`).
- `humidity`: Porcentagem de umidade formatada (`str`).
- `moon_phase`: Porcentagem de iluminação da Lua (`str`).

#### `PlanetVisibility`

Indica a posição e status de observação de um planeta ou satélite.

- `name`: Nome do corpo celeste (`str`).
- `detail`: Posição formatada (ex: `"Alt. 62°  ·  Az. 188°"`).
- `status`: Cor de status do semáforo: `"green"`, `"yellow"`, ou `"red"`.

---

## Uso

```python
from sky_observer.services.observation_service import ObservationService

service = ObservationService()

# 1. Busca de localidade
city = service.search_location("São Paulo")
if city:
    # 2. Obter condições integradas (Clima + Skyfield)
    result = service.get_conditions(city.latitude, city.longitude, city.name)

    print(f"Status em {result.location}: {result.status} (Nota {result.score}/100)")
    print(f"Cobertura de Nuvens: {result.metrics.cloud_cover}%")

    for planet in result.planets:
        print(f"- {planet.name}: {planet.detail} ({planet.status})")
```

---

## Integração com a UI (Tkinter) e Concorrência 🧵

Como as chamadas ao `ObservationService` envolvem requisições de rede (Open-Meteo) e cálculos de efemérides (Skyfield), executá-las diretamente na Thread principal do Tkinter fará a interface congelar temporariamente.

A melhor prática é executar as consultas em uma **Thread em segundo plano (Background Thread)** e atualizar a interface na Thread principal assim que os dados chegarem.

### Exemplo de Integração Segura com Threads

Abaixo está um exemplo de como implementar essa integração em `main_window.py`:

```python
import threading
from tkinter import messagebox
from sky_observer.services.observation_service import ObservationService

# No __init__ da MainWindow, instancie o serviço uma única vez:
# self.observation_service = ObservationService()

def _on_date_click(self, date_type):
    # 1. Mostra um feedback visual de carregamento na tela
    self.frames["conditions"].widgets["sem_title"].config(text="Carregando dados...")
    self.frames["conditions"].set_active_date(date_type)

    # 2. Define a função que rodará na Thread de background
    def run_query():
        try:
            # Pega as coordenadas ativas (exemplo: Curitiba)
            lat, lon = -25.4284, -49.2733

            # Executa a chamada bloqueante de I/O e CPU
            result = self.observation_service.get_conditions(lat, lon, "Curitiba")

            # Converte o retorno em dicionário conforme o esperado pela View
            ui_data = {
                "is_object_context": False,
                "location": result.location,
                "score": result.score,
                "status": result.status,
                "title": result.title,
                "subtitle": result.subtitle,
                "metrics": {
                    "cloud_cover": result.metrics.cloud_cover,
                    "seeing": result.metrics.seeing,
                    "humidity": result.metrics.humidity,
                    "moon_phase": result.metrics.moon_phase,
                },
                "planets": [
                    {
                        "name": p.name,
                        "detail": p.detail,
                        "status": p.status
                    }
                    for p in result.planets
                ]
            }

            # 3. Agenda a atualização na thread principal do Tkinter de forma segura
            self.root.after(0, lambda: self.frames["conditions"].update_display(ui_data))

        except Exception as e:
            # Em caso de erro, agenda exibição de mensagem na thread principal
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Falha ao carregar: {e}"))

    # 4. Inicia a Thread como Daemon (para fechar automaticamente se o app fechar)
    thread = threading.Thread(target=run_query, daemon=True)
    thread.start()
```

### Por que isso é importante?

1. **Responsividade da Interface**: A interface do Tkinter continua aceitando interações, permitindo arrastar a janela, redimensionar e clicar em outras seções enquanto a rede responde.
2. **Uso de `.after(ms, callback)`**: O Tkinter **não é thread-safe**. Tentar acessar ou modificar propriedades de widgets de dentro de uma thread paralela pode causar falhas silenciosas, segfaults ou travamentos inesperados. O `.after(0, ...)` agenda o callback para rodar de forma segura na thread principal do loop do Tkinter (`mainloop`).
3. **Mapeamento Explícito**: Converte a tipagem estática e imutável das Dataclasses do Back-end no dicionário bruto (tipo JSON) esperado dinamicamente pela arquitetura de views do Front-end.

---

## Testes

O módulo de serviços é coberto por testes unitários focados na validação das regras de negócio, lógica de pontuação e orquestração de dependências:

- `test_search_location`: Valida se a transformação do resultado do geocodificador ocorre sem problemas.
- `test_calculate_score`: Verifica o cálculo sob diferentes condições meteorológicas (perfeitas, intermediárias e péssimas).
- `test_score_to_status`: Verifica os limiares de conversão das notas para as classificações de status da UI.
- `test_get_conditions`: Orquestra mocks do `OpenMeteoClient` e `SkyFieldClient` para garantir que o cruzamento de dados, formatação e status do semáforo visual funcionam como esperado de ponta a ponta.

Para rodar os testes da camada de serviços:

```bash
uv run pytest test/services/observation_service_test.py -v
```
