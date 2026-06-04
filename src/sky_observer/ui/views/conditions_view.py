import tkinter as tk
from tkinter import ttk

from sky_observer.ui.theme import COLORS, FONTS


class ConditionsView(tk.Frame):
  """
  Tela principal: semáforo, métricas e lista de planetas.
  """

  def __init__(self, parent):
    super().__init__(parent, bg=COLORS["bg_primary"])
    # Dicionário para guardar referências apenas dos widgets que vão mudar de valor/texto.
    self.widgets = {}
    self._build()

  def _build(self):
    self._create_topbar()
    self._create_scrollable_content()

  # ── Topbar ────────────────────────────────────────────
  def _create_topbar(self):
    bar = tk.Frame(self, bg=COLORS["bg_primary"], pady=12)
    bar.pack(fill=tk.X, padx=20)

    left_frame = tk.Frame(bar, bg=COLORS["bg_primary"])
    left_frame.pack(side=tk.LEFT)

    self.widgets["btn_back"] = tk.Label(
      left_frame,
      text="← Voltar à Busca",
      font=FONTS["small"],
      bg=COLORS["bg_secondary"],
      fg=COLORS["text_primary"],
      padx=10,
      pady=4,
      cursor="hand2",
    )
    # O botão voltar inicia oculto

    self.widgets["main_title"] = tk.Label(
      left_frame,
      text="Condições de observação",
      font=FONTS["title"],
      bg=COLORS["bg_primary"],
      fg=COLORS["text_primary"],
    )
    self.widgets["main_title"].pack(side=tk.LEFT)

    # Lado direito: localização + datas
    right = tk.Frame(bar, bg=COLORS["bg_primary"])
    right.pack(side=tk.RIGHT)

    self._location_pill(right)
    self._date_buttons(right)

    # Linha separadora
    tk.Frame(self, bg=COLORS["border"], height=1).pack(fill=tk.X)

  def _location_pill(self, parent):
    pill = tk.Label(
      parent,
      text="📍 Selecione um local  ▾",
      font=FONTS["small"],
      bg=COLORS["bg_primary"],
      fg=COLORS["text_secondary"],
      padx=10,
      pady=5,
      relief="flat",
      cursor="hand2",
    )
    pill.pack(side=tk.LEFT, padx=(0, 10))
    # Borda manual via highlight
    pill.config(highlightbackground=COLORS["border"], highlightthickness=1)
    self.widgets["location"] = pill

  def _date_buttons(self, parent):
    btn_today = tk.Label(
      parent,
      text="Hoje",
      font=FONTS["small"],
      bg=COLORS["blue_bg"],
      fg=COLORS["blue"],
      padx=10,
      pady=4,
    )
    btn_today.pack(side=tk.LEFT, padx=2)

  def bind_events(self, on_location_click, on_back_click=None):
    """
    Conecta os eventos de clique desta view às funções do controlador (MainWindow).
    Isso garante que a View não toma decisões de negócio, apenas "avisa" que algo foi clicado.
    """
    if "location" in self.widgets:
      self.widgets["location"].bind("<Button-1>", lambda e: on_location_click())
    if "btn_back" in self.widgets:
      self.widgets["btn_back"].bind(
        "<Button-1>", lambda e: on_back_click() if on_back_click else None
      )

  # ── Área rolável ──────────────────────────────────────
  def _create_scrollable_content(self):
    """Cria um canvas com scrollbar para o conteúdo principal."""
    container = tk.Frame(self, bg=COLORS["bg_primary"])
    container.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(container, bg=COLORS["bg_primary"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Frame interno onde o conteúdo real fica
    self.inner = tk.Frame(canvas, bg=COLORS["bg_primary"])
    canvas_window = canvas.create_window((0, 0), window=self.inner, anchor="nw")

    # Ajusta o scroll quando o conteúdo muda de tamanho
    def on_resize(e):
      canvas.configure(scrollregion=canvas.bbox("all"))
      canvas.itemconfig(canvas_window, width=canvas.winfo_width())

    self.inner.bind("<Configure>", on_resize)
    canvas.bind("<Configure>", on_resize)

    # Scroll com o mouse
    canvas.bind_all(
      "<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units")
    )

    self._create_content(self.inner)

  # ── Conteúdo ──────────────────────────────────────────
  def _create_content(self, parent):
    self._create_semaphore_card(parent)
    self._create_metrics_grid(parent)
    self._create_planets_section(parent)

  # ── Card semáforo ─────────────────────────────────────
  def _create_semaphore_card(self, parent):
    card = tk.Frame(
      parent,
      bg=COLORS["bg_primary"],
      highlightbackground=COLORS["border"],
      highlightthickness=1,
      pady=16,
      padx=16,
    )
    card.pack(fill=tk.X, padx=20, pady=(16, 0))

    # Círculo colorido (Canvas)
    circle_canvas = tk.Canvas(
      card, width=70, height=70, bg=COLORS["bg_primary"], highlightthickness=0
    )
    circle_canvas.pack(side=tk.LEFT, padx=(0, 16))

    self.widgets["sem_canvas"] = circle_canvas
    self.widgets["sem_oval"] = circle_canvas.create_oval(
      4, 4, 66, 66, fill=COLORS["bg_secondary"], outline=COLORS["border"], width=2
    )
    self.widgets["sem_icon"] = circle_canvas.create_text(
      35, 35, text="...", font=("Helvetica", 22, "bold"), fill=COLORS["text_muted"]
    )

    # Texto central
    info = tk.Frame(card, bg=COLORS["bg_primary"])
    info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.widgets["sem_title"] = tk.Label(
      info,
      text="Avaliando as condições...",
      font=FONTS["title"],
      bg=COLORS["bg_primary"],
      fg=COLORS["text_primary"],
      anchor="w",
    )
    self.widgets["sem_title"].pack(fill=tk.X)

    self.widgets["sem_subtitle"] = tk.Label(
      info,
      text="Aguarde, processando dados",
      font=FONTS["body"],
      bg=COLORS["bg_primary"],
      fg=COLORS["text_secondary"],
      anchor="w",
    )
    self.widgets["sem_subtitle"].pack(fill=tk.X, pady=(4, 0))

    # Pontuação à direita
    score_frame = tk.Frame(card, bg=COLORS["bg_primary"])
    score_frame.pack(side=tk.RIGHT, padx=(16, 0))

    self.widgets["score_val"] = tk.Label(
      score_frame,
      text="--",
      font=FONTS["score"],
      bg=COLORS["bg_primary"],
      fg=COLORS["text_muted"],
    )
    self.widgets["score_val"].pack()

    tk.Label(
      score_frame,
      text="/ 100",
      font=FONTS["small"],
      bg=COLORS["bg_primary"],
      fg=COLORS["text_muted"],
    ).pack()

  # ── Grid de métricas ──────────────────────────────────
  def _create_metrics_grid(self, parent):
    grid = tk.Frame(parent, bg=COLORS["bg_primary"])
    grid.pack(fill=tk.X, padx=20, pady=12)

    # Configura 4 colunas iguais
    for i in range(4):
      grid.columnconfigure(i, weight=1, uniform="metrics")

    metrics = [
      ("cloud_cover", "☁️", "Cobertura", "%"),
      ("seeing", "👁️", "Seeing", "/8"),
      ("humidity", "💧", "Umidade", "%"),
      ("moon_phase", "🌙", "Lua", "%"),
    ]

    for col, (key, icon, label, unit) in enumerate(metrics):
      self._metric_card(grid, key, icon, label, unit, col)

  def _metric_card(self, parent, key, icon, label, unit, column):
    card = tk.Frame(
      parent,
      bg=COLORS["bg_secondary"],
      padx=12,
      pady=12,
    )
    card.grid(row=0, column=column, padx=(0, 8) if column < 3 else 0, sticky="nsew")

    # Ícone + rótulo
    tk.Label(
      card,
      text=f"{icon}  {label}",
      font=FONTS["small"],
      bg=COLORS["bg_secondary"],
      fg=COLORS["text_secondary"],
      anchor="w",
    ).pack(fill=tk.X)

    # Valor + unidade
    value_frame = tk.Frame(card, bg=COLORS["bg_secondary"])
    value_frame.pack(fill=tk.X, pady=(6, 0))

    val_label = tk.Label(
      value_frame,
      text="--",
      font=FONTS["metric"],
      bg=COLORS["bg_secondary"],
      fg=COLORS["text_primary"],
    )
    val_label.pack(side=tk.LEFT)
    self.widgets[f"metric_{key}"] = val_label

    tk.Label(
      value_frame,
      text=unit,
      font=FONTS["small"],
      bg=COLORS["bg_secondary"],
      fg=COLORS["text_muted"],
    ).pack(side=tk.LEFT, padx=(3, 0), pady=(6, 0))

  # ── Lista de planetas ─────────────────────────────────
  def _create_planets_section(self, parent):
    section = tk.Frame(parent, bg=COLORS["bg_primary"])
    section.pack(fill=tk.X, padx=20, pady=(4, 20))

    tk.Label(
      section,
      text="Planetas visíveis esta noite",
      font=FONTS["small"],
      bg=COLORS["bg_primary"],
      fg=COLORS["text_secondary"],
    ).pack(anchor="w", pady=(0, 8))

    self.planets_list_frame = tk.Frame(section, bg=COLORS["bg_primary"])
    self.planets_list_frame.pack(fill=tk.X)

  def _planet_row(self, parent, name, detail, status):
    row = tk.Frame(
      parent,
      bg=COLORS["bg_primary"],
      highlightbackground=COLORS["border"],
      highlightthickness=1,
      padx=12,
      pady=10,
    )
    row.pack(fill=tk.X, pady=(0, 6))

    # Dot colorido
    dot_color = {
      "green": COLORS["green"],
      "yellow": COLORS["yellow"],
      "red": COLORS["red"],
    }[status]

    dot = tk.Canvas(
      row, width=10, height=10, bg=COLORS["bg_primary"], highlightthickness=0
    )
    dot.pack(side=tk.LEFT, padx=(0, 10))
    dot.create_oval(1, 1, 9, 9, fill=dot_color, outline="")

    # Nome
    tk.Label(
      row,
      text=name,
      font=FONTS["subtitle"],
      bg=COLORS["bg_primary"],
      fg=COLORS["text_primary"],
      width=9,
      anchor="w",
    ).pack(side=tk.LEFT)

    # Detalhe
    tk.Label(
      row,
      text=detail,
      font=FONTS["small"],
      bg=COLORS["bg_primary"],
      fg=COLORS["text_secondary"],
      anchor="w",
    ).pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Badge de status
    badge_colors = {
      "green": (COLORS["green_bg"], COLORS["green_text"], "Visível"),
      "yellow": (COLORS["yellow_bg"], COLORS["yellow_text"], "Baixo"),
      "red": (COLORS["red_bg"], COLORS["red_text"], "Invisível"),
    }
    bg, fg, text = badge_colors[status]

    tk.Label(
      row,
      text=text,
      font=FONTS["small"],
      bg=bg,
      fg=fg,
      padx=8,
      pady=2,
    ).pack(side=tk.RIGHT)

  # ── Lógica de Atualização (Data-Driven) ────────────────
  def update_display(self, data: dict):
    """
    Atualiza a interface visual consumindo um dicionário de dados.
    Isso permite que a View seja "Data-Driven" e não precise conhecer a lógica do OpenMeteo.
    """
    if "is_object_context" in data:
      if data["is_object_context"]:
        self.widgets["btn_back"].pack(
          side=tk.LEFT, padx=(0, 12), before=self.widgets["main_title"]
        )
        self.widgets["main_title"].config(text="Análise do Objeto")
      else:
        self.widgets["btn_back"].pack_forget()
        self.widgets["main_title"].config(text="Condições de observação")

    if "location" in data:
      self.widgets["location"].config(text=f"📍 {data['location']}  ▾")

    # Atualiza métricas base do semáforo
    if "score" in data:
      self.widgets["score_val"].config(text=str(data["score"]))
    if "title" in data:
      self.widgets["sem_title"].config(text=data["title"])
    if "subtitle" in data:
      self.widgets["sem_subtitle"].config(text=data["subtitle"])

    # Atualiza visual do semáforo (cores e ícones)
    if "status" in data:
      st = data["status"]
      canvas = self.widgets["sem_canvas"]
      if st == "good":
        canvas.itemconfig(
          self.widgets["sem_oval"], fill=COLORS["green_bg"], outline=COLORS["green"]
        )
        canvas.itemconfig(self.widgets["sem_icon"], text="✓", fill=COLORS["green"])
        self.widgets["score_val"].config(fg=COLORS["green"])
      elif st == "fair":
        canvas.itemconfig(
          self.widgets["sem_oval"], fill=COLORS["yellow_bg"], outline=COLORS["yellow"]
        )
        canvas.itemconfig(self.widgets["sem_icon"], text="!", fill=COLORS["yellow"])
        self.widgets["score_val"].config(fg=COLORS["yellow"])
      elif st == "bad":
        canvas.itemconfig(
          self.widgets["sem_oval"], fill=COLORS["red_bg"], outline=COLORS["red"]
        )
        canvas.itemconfig(self.widgets["sem_icon"], text="✕", fill=COLORS["red"])
        self.widgets["score_val"].config(fg=COLORS["red"])

    # Atualiza grade de 4 métricas
    if "metrics" in data:
      for key, value in data["metrics"].items():
        widget_key = f"metric_{key}"
        if widget_key in self.widgets:
          self.widgets[widget_key].config(text=str(value))

    # Reconstrói a lista de planetas
    if "planets" in data:
      for widget in self.planets_list_frame.winfo_children():
        widget.destroy()

      for p in data["planets"]:
        self._planet_row(self.planets_list_frame, p["name"], p["detail"], p["status"])

  def _load_dummy_data(self):
    """Preenche a tela com dados falsos apenas para visualização."""
    self.update_display(
      {
        "is_object_context": False,
        "location": "Teresina, PI",
        "score": 87,
        "status": "good",
        "title": "Ótimo para observar",
        "subtitle": "Céu limpo, seeing excelente e planetas visíveis",
        "metrics": {
          "cloud_cover": "12",
          "seeing": "7",
          "humidity": "48",
          "moon_phase": "23",
        },
        "planets": [
          {
            "name": "Saturno",
            "detail": "Alt. 62°  ·  Az. 188°  ·  20h15 – 02h30",
            "status": "green",
          },
          {
            "name": "Júpiter",
            "detail": "Alt. 44°  ·  Az. 210°  ·  21h00 – 03h10",
            "status": "green",
          },
          {
            "name": "Marte",
            "detail": "Alt. 18°  ·  Az. 270°  ·  04h00 – 05h40",
            "status": "yellow",
          },
          {"name": "Vênus", "detail": "Abaixo do horizonte até 05h50", "status": "red"},
        ],
      }
    )
