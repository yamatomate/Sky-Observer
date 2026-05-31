# 🛠️ Tarefas de Integração: Back-End para UI

Este documento detalha o que precisa ser feito pelo Back-End para dar "vida" à interface do **Sky Observer**. Toda a estrutura de UI já está pronta e desacoplada, aguardando apenas a injeção dos dados reais.

O único arquivo que você precisará modificar é o **`src/sky_observer/ui/main_window.py`**.

---

## Passo 1: Instanciar os Clientes (APIs)
Os clientes do OpenMeteo e Skyfield realizam requisições de rede ou carregam arquivos pesados (`.bsp`). Portanto, eles devem ser instanciados apenas **uma vez**.

**Onde alterar:** No método `__init__` da classe `MainWindow`.

**O que fazer:**
1. Importe `OpenMeteoClient` e `SkyFieldClient`.
2. Crie instâncias dessas classes em propriedades da `MainWindow` (ex: `self.weather_client = OpenMeteoClient()`).
3. *Nota:* Para o SkyField, você precisará de uma latitude/longitude inicial padrão (ex: pegue via `search_location` do OpenMeteo para uma cidade base, ou deixe fixo por enquanto).

---

## Passo 2: Alimentar a Tela de Condições (Clima + Planetas)
Quando o usuário clica em "Hoje" ou "Amanhã", a função `_on_date_click` é chamada. Ela precisa buscar o clima atual e a posição dos planetas, juntar tudo e enviar para a tela.

**Onde alterar:** Método `_on_date_click(self, date_type)` na `MainWindow`.

**O que fazer:**
1. Chame `self.weather_client.get_weather(...)` para pegar o clima.
2. Chame a lógica do `self.skyfield_client` para descobrir quais planetas estão visíveis agora.
3. Monte um dicionário **exatamente** com a estrutura abaixo.
4. Chame `self.frames["conditions"].update_display(dados_condicoes)`.

### Formato Exigido pela View:
```python
dados_condicoes = {
    "is_object_context": False, # Enviar sempre False aqui na visão geral
    "location": "Teresina, PI", # Pegue de um estado ou LocationResponse
    "score": 87,                # Lógica: Calcule de 0 a 100 baseado no clima
    "status": "good",           # Mapeamento visual: "good", "fair", ou "bad"
    "title": "Ótimo para observar", # Título que desejar
    "subtitle": weather_response.weather_description, # Vem direto do WMO_CODES
    "metrics": {
        "cloud_cover": str(weather_response.cloud_cover_pct),
        "seeing": "7",                    # Calcular ou fixar por enquanto
        "humidity": str(weather_response.humidity_pct),
        "moon_phase": "23",               # Pegar do Skyfield se possível
    },
    "planets": [
        {
            # Para cada planeta na lista de observáveis do SkyField
            "name": "Saturno", 
            "detail": f"Alt. {altitude.degrees:.0f}° · Az. {azimuth.degrees:.0f}°", 
            "status": "green" if visible else "red" # Cores: "green", "yellow", "red"
        }
    ]
}
```

---

## Passo 3: Alimentar a Tela de Busca de Objetos
Quando o usuário digita algo e clica em "Buscar", a UI entrega a string no método `_on_search_objects`.

**Onde alterar:** Método `_on_search_objects(self, query)` na `MainWindow`.

**O que fazer:**
1. Use o `self.skyfield_client.search_object(query)`.
2. Formate a resposta e envie os resultados num dicionário como abaixo.
3. Chame `self.frames["objects"].update_display(dados_busca)`.

### Formato Exigido pela View:
```python
dados_busca = {
    "results": [
        {
            "icon": "🪐", 
            "name": query.capitalize(), 
            "type": "Objeto Celeste", 
            "details": f"Alt: {alt:.1f}° | Visível: {'Sim' if vis else 'Não'}"
        }
    ]
}
```

---

## Passo 4: Alimentar a Tela Contextual (Condições de um único objeto)
Quando o usuário clica num objeto na tela de Busca, ele é levado de volta para as Condições, mas o foco agora é só aquele planeta.

**Onde alterar:** Método `_on_object_select(self, item)` na `MainWindow`.

**O que fazer:**
A lógica atual desse método já possui o dicionário "falso" sendo passado (Mock). Você só precisa trocar os dados *fake* pelos cálculos que acabamos de mostrar no Passo 2 e 3.
*Atenção:* O campo `"is_object_context"` **deve ser True** aqui para exibir o botão de voltar!

---

## Dicas Finais
- Fique à vontade para apagar as chamadas de `messagebox.showinfo` nos eventos da `main_window.py`. Elas eram apenas avisos provisórios da UI.
- Ao terminar a integração, retire o `self._load_dummy_data()` que está dentro dos arquivos da pasta `views`. 