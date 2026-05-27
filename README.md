# Sky Observer

Avalia o clima e a qualidade do céu em tempo real com base na sua localização. Identifica objetos celestes visíveis e fornece instruções para calibração do telescópio.

## Requisitos

- Python 3.13+
- [UV](https://docs.astral.sh/uv/)

## Instalação

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Confirme a instalação:
```bash
uv --version
```

## Como usar

Instale as dependências:
```bash
uv sync
```

Execute o projeto:
```bash
uv run start
```

## Comandos úteis

| Comando | O que faz |
|---|---|
| `uv sync` | Instala/atualiza dependências |
| `uv run start` | Executa o projeto |
| `uv add <pacote>` | Adiciona nova dependência |
| `uv remove <pacote>` | Remove dependência |
| `uv tree` | Mostra árvore de dependências |

## Estrutura

```
sky-observer/
├── src/
│   └── sky_observer/
│       ├── __init__.py
│       ├── main.py
│       └── infra/
│           ├── openmeteo/
│           └── skyfield/
├── pyproject.toml
└── README.md
```
