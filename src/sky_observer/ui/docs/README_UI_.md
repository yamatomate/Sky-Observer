# 🎨 Arquitetura de Interface (UI) - Sky Observer

Este documento explica a estrutura, os padrões de projeto e as decisões de engenharia adotadas na camada de interface gráfica (Front-End) do **Sky Observer**, construída com `tkinter`.

A nossa principal meta na construção desta interface foi **desacoplar completamente o visual da lógica de negócios**, garantindo uma aplicação rápida, testável e pronta para receber a integração com APIs externas (como a OpenMeteo e Skyfield) sem gerar código espaguete.

---

## 🏗️ Padrão Arquitetural

Adotamos uma abordagem inspirada no padrão **MVC (Model-View-Controller)**, focada em manter as telas "burras" e centralizar as decisões.

### 1. O Controlador (`main_window.py`)
A classe `MainWindow` atua como o maestro da interface.
- **Gerencia o Estado:** Ela é a única que conhece todas as telas e a barra lateral.
- **Navegação (Estilo SPA):** Em vez de destruir e recriar telas a cada clique (o que consome processamento e perde os dados preenchidos), todas as telas são instanciadas uma única vez no método `_init_frames()`. Elas são empilhadas na mesma célula usando `.grid(row=0, column=0)`. A navegação acontece usando o comando `.tkraise()`, que apenas traz a tela desejada para frente, criando uma transição instantânea e fluida.
- **Delegação de Eventos:** Todos os cliques de botões das Views disparam eventos (callbacks) que são tratados aqui. É neste arquivo que a equipe de backend deve injetar o código que consome as APIs.

### 2. As Telas / Views (`views/`)
As classes na pasta `views` (`ConditionsView`, `ObjectsView`, `LocationsView`) são estritamente visuais.
- **Data-Driven (Orientadas a Dados):** Nenhuma View consome APIs ou faz cálculos. Elas possuem um método `update_display(data: dict)` que recebe as informações mastigadas em um dicionário e as injeta nos componentes do Tkinter (`Labels`, `Canvas`, etc.).
- **Encapsulamento de Widgets:** Apenas os elementos que mudam de valor dinamicamente (números, cores, textos de status) são salvos em memória num dicionário interno chamado `self.widgets = {}`. Isso mantém a classe leve.
- **Delegação Limpa:** As Views não sabem o que fazer quando um botão é clicado. Elas possuem um método `bind_events()` onde o Controlador injeta as funções de resposta. A View apenas avisa: *"Fui clicada, faça o que tiver que ser feito"*.

### 3. Componentes e Estilização (`components/` e `theme.py`)
- Componentes reutilizáveis, como a `Sidebar`, vivem isolados e gerenciam seus próprios micro-estados (como acender a cor azul no menu ativo, ou responder ao *hover* do mouse).
- Cores, fontes e espaçamentos não ficam "hardcoded" (soltos) no código. Eles são importados de `theme.py`, permitindo no futuro até mesmo a criação rápida de um "Modo Escuro" alterando apenas um arquivo.

---

## 🧠 Por que não usar `destroy()` nas Views?

O Tkinter tradicionalmente encoraja o desenvolvedor a usar `widget.destroy()` e recriar toda a tela sempre que o usuário muda de aba. No entanto, no **Sky Observer** optamos por inicializar tudo no `_init_frames()` e usar o empilhamento em Grade (`grid`) em conjunto com o `.tkraise()`.

**Motivos:**
1. **Performance:** Evita sobrecarga de memória (Garbage Collection) ao destruir e alocar objetos repetidamente.
2. **Preservação de Estado:** Se o usuário rolar a barra da `ConditionsView` para baixo e mudar para a aba `ObjectsView`, ao voltar, a rolagem estará exatamente onde ele deixou. Em telas de formulário, isso previne a perda do que já foi digitado.

---

## 🤝 Guia de Desenvolvimento e Integração

Se você precisa conectar dados reais de API, ou criar novas funcionalidades dentro dessa arquitetura, preparamos um arquivo de regras separadas. Ele atuará como o contrato de comunicação entre o backend e a interface visual.
👉 **Leia o documento: INTEGRATION_GUIDE.md**

---

## 📂 Resumo da Estrutura de Arquivos da UI

```text
ui/
├── README.md               # 👈 Você está aqui
├── main_window.py          # Controlador Principal e layout da Janela
├── theme.py                # Cores, fontes e constantes de design
│
├── components/             # Componentes reaproveitáveis
│   └── sidebar.py          # Barra lateral e sistema de menu
│
└── views/                  # Telas do sistema
    ├── conditions_view.py  # Tela de semáforo e métricas de clima
    ├── objects_view.py     # Tela de busca (Skyfield)
    └── locations_view.py   # Tela de gerenciamento de cidades favoritos
```

---

*Arquitetura projetada visando manutenibilidade, separação de responsabilidades (SoC) e testes contínuos.*