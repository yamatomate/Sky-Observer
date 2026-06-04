# Sky Observer

Avalie o clima e a qualidade do céu em tempo real para as suas observações astronômicas. O Sky Observer identifica objetos celestes visíveis na sua localização e fornece instruções passo a passo para a calibração do seu telescópio.

---

## 🚀 Como Baixar e Usar (Sem Instalar Nada)

Você não precisa instalar o Python ou configurar códigos para usar o Sky Observer. Basta acessar a página de [Releases](https://github.com/yamatomate/Sky-Observer/releases) e baixar a versão pronta para o seu sistema operacional:

- **Windows:** Baixe o arquivo `.exe` e execute-o diretamente.
- **Linux:** Baixe o arquivo `.tar.gz`, descompacte-o e execute o binário.
- **macOS Apple Silicon (M1/M2/M3):** Baixe o arquivo `.zip`, descompacte-o e execute o aplicativo.
- **macOS Intel:** Baixe o arquivo `.zip`, descompacte-o e execute o aplicativo.

*Nota para macOS/Linux: Dependendo das configurações do seu sistema, pode ser necessário dar permissão de execução ao binário (`chmod +x SkyObserver`).*

---

## 🌟 Funcionalidades Principais

- **Condições de Observação:** Análise detalhada de cobertura de nuvens, umidade, temperatura e vento em tempo real para saber se o céu está limpo.
- **Objetos Celestes Visíveis:** Lista instantânea de planetas e astros visíveis no céu na sua posição geográfica atual.
- **Calibração de Telescópio:** Guia interativo passo a passo para alinhar e ajustar seu equipamento.
- **Gerenciador de Localizações:** Salve e alterne rapidamente entre seus pontos favoritos de observação.

---

## 💻 Configuração para Desenvolvimento

Se você deseja rodar o projeto a partir do código-fonte ou contribuir com o desenvolvimento:

### Requisitos
- Python 3.13+
- Gerenciador [UV](https://astral.sh) instalado no sistema

### Passos para Início Rápido
```bash
# Clone o repositório
git clone https://github.com/yamatomate/Sky-Observer.git
cd Sky-Observer

# Sincronize as dependências e inicie o aplicativo
uv sync
uv run start
```

### Comandos Úteis
- **Iniciar em Desenvolvimento:** `uv run start`
- **Bumping de Versão:** `uv run bump [patch|minor|major]`
- **Compilar Executável Local:** `uv run build [--console] [--onedir]`

---

## 🤖 Integração e Entrega Contínua (CI/CD)

Toda tag enviada ao repositório no formato `v*` (ex: `v1.0.0`) dispara automaticamente o GitHub Actions, que compila todos os executáveis listados acima nativamente e os anexa à aba de Releases do GitHub.
