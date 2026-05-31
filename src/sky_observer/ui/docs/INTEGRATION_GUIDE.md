# 🔌 Guia de Integração Back-End e Front-End

Olá, dev! 👋

Se você chegou até aqui, provavelmente é sua missão conectar os dados reais do **OpenMeteo** ou do **Skyfield** na interface gráfica do *Sky Observer*. 

A UI (Front-End) foi modelada usando padrões rigorosos de engenharia de software para que você **não precise** aprender detalhes difíceis do Tkinter. Siga este guia rápido para fazer a integração dar certo de primeira, sem gerar "código espaguete".

---

## 1. As Regras de Ouro (A Muralha de Separação) 🛡️

Para garantir que nosso projeto continue organizado e fácil de dar manutenção:

*   **Sem Tkinter no Back-end:** O seu código (nas pastas `infra` ou `core`) **nunca** deve importar a biblioteca `tkinter` ou tentar alterar uma cor/texto da tela diretamente. A responsabilidade visual é exclusiva da pasta `ui`.
*   **A Interface é "Burra":** A UI não calcula constelações nem formata strings de API. Ela só espera receber um dicionário pronto e o desenha na tela. O processamento é responsabilidade do Back-end.
*   **Carga na Inicialização:** O `OpenMeteoClient` e o carregamento das efemérides (arquivos `.bsp` do Skyfield) podem ser operações pesadas. **Não instancie** essas classes a cada clique do usuário! Crie os clientes uma vez só no método `__init__` da `MainWindow` e os reutilize.
*   **Cuidado com a Thread Principal:** O Tkinter pausa a tela enquanto espera a sua função terminar. O cache do OpenMeteo que você já implementou (`niquests_cache`) vai ajudar imensamente nisso, mas mantenha a responsividade da API sempre em mente.
*   **Tratamento Amigável:** Se a API cair ou não encontrar a cidade, não retorne exceções brutas. Capture o erro e dispare um alerta visual seguro. Exemplo: `if not data: messagebox.showerror("Erro", "Sem conexão")`.

---

## 2. Onde eu coloco a minha lógica? 🧩

Toda a interação do usuário deságua no arquivo principal do controlador da UI: `main_window.py`. 
Vá até a sessão comentada com **`Controladores de Eventos`** no final do arquivo. É lá que você vai interceptar os cliques.

Lá estão funções prontas aguardando o seu código:
*   `_on_location_click()`
*   `_on_date_click(date_type)`
*   `_on_search_objects(query)`

---

## 3. Como eu envio os dados para a Tela? 📡

Depois de buscar e processar os dados nas suas classes `infra`, você só precisa chamar a função `update_display(dicionário_de_dados)` da tela que você quer atualizar.

**Exemplo prático de integração na tela de Condições (`_on_date_click`):**

```python
# Em main_window.py

def _on_date_click(self, date_type):
    # 1. Altera a cor do botão na interface para mostrar o menu atual
    self.frames["conditions"].set_active_date(date_type)
    
    # 2. Busque os dados reais na infraestrutura
    # weather = open_meteo_client.get_weather(-5.0892, -42.8019)
    
    # 3. Traduza a dataclass do Back-end (WeatherDataResponse) para um Dicionário Visual 
    ui_data = {
        "location": "Teresina, PI",
        "score": 87, # Implementar cálculo final
        "status": "good", # Gatilho visual: "good", "fair", ou "bad"
        "title": "Ótimo para observar",
        "subtitle": weather.weather_description,
        "metrics": {
            "cloud_cover": weather.cloud_cover_pct,
            "seeing": "7",
            "humidity": weather.humidity_pct,
            "moon_phase": "23",
        },
        "planets": [{"name": "Saturno", "detail": "Alt. 62°...", "status": "green"}]
    }
    
    # 4. Entregue os dados mastigados para a View! Ela fará a mágica acontecer.
    self.frames["conditions"].update_display(ui_data)
```

> **⚠️ Último Passo Crítico:** Quando você começar a plugar os dados na `MainWindow`, abra os arquivos da pasta `views/` (ex: `conditions_view.py`) e remova a chamada `self._load_dummy_data()` no final da função `__init__`. Nós os usamos apenas para testes visuais de Front-End e eles devem sair antes da aplicação ir para produção.