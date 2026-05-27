# Sky Observer

## Sobre

Usando sua localização, nosso app avalia o clima e a qualidade do céu em tempo real. Encontre objetos celestes visíveis e receba instruções simples para calibrar seu telescópio.

## Como executar o projeto

### 1. Instalar o UV

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> Confirme que instalou rodando `uv --version`.

### 2. Instalar as dependências

Na raiz do projeto, execute:

```bash
uv sync
```

Isso cria o ambiente virtual (`.venv`) e baixa todas as dependências listadas no `pyproject.toml`.

### 3. Rodar o projeto

```bash
uv run python src/main.py
```

Só isso. O `uv run` executa no ambiente virtual automaticamente

### Comandos úteis

| Comando | O que faz |
|---|---|
| `uv sync` | Instala/atualiza dependências |
| `uv add <pacote>` | Adiciona nova dependência |
| `uv remove <pacote>` | Remove dependência |
| `uv run <comando>` | Executa sem ativar o venv |
| `uv tree` | Mostra árvore de dependências |
