import tkinter as tk
from sky_observer.ui.theme import COLORS, FONTS


class ObjectsView(tk.Frame):
    """
    Tela para busca e listagem de objetos celestes (Planetas, Estrelas, etc.).
    """

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_primary"])
        # Guarda referências de elementos interativos (campo de busca e botão)
        self.widgets = {}
        self._build()
        self._load_dummy_data()

    def _build(self):
        self._create_topbar()
        self._create_search_bar()
        self._create_results_area()

    # ── Topbar ────────────────────────────────────────────
    def _create_topbar(self):
        bar = tk.Frame(self, bg=COLORS["bg_primary"], pady=12)
        bar.pack(fill=tk.X, padx=20)

        tk.Label(
            bar,
            text="Busca de Objetos",
            font=FONTS["title"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
        ).pack(side=tk.LEFT)

        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill=tk.X)

    # ── Barra de Busca ────────────────────────────────────
    def _create_search_bar(self):
        search_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=16)
        search_frame.pack(fill=tk.X, padx=20)

        # Campo de digitação
        entry = tk.Entry(
            search_frame,
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["border"]
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, ipadx=8)
        self.widgets["search_entry"] = entry

        # Botão buscar
        btn_search = tk.Label(
            search_frame,
            text="🔍 Buscar",
            font=FONTS["small"],
            bg=COLORS["blue_bg"],
            fg=COLORS["blue"],
            padx=16,
            pady=6,
            cursor="hand2"
        )
        btn_search.pack(side=tk.LEFT, padx=(12, 0))
        self.widgets["btn_search"] = btn_search

    def bind_events(self, on_search, on_object_select=None):
        """
        Conecta o clique do botão de busca à MainWindow, repassando
        o texto que o usuário digitou no campo 'search_entry'.
        """
        if "btn_search" in self.widgets:
            self.widgets["btn_search"].bind(
                "<Button-1>", 
                lambda e: on_search(self.widgets["search_entry"].get())
            )
        self.widgets["on_object_select"] = on_object_select

    # ── Área de Resultados ────────────────────────────────
    def _create_results_area(self):
        self.results_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=20)

    def update_display(self, data: dict):
        """
        Limpa os resultados anteriores e recria os cards na tela 
        com base na nova lista de resultados repassada pelo controlador.
        """
        # Limpa os resultados anteriores
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Renderiza os novos resultados
        for item in data.get("results", []):
            self._create_object_card(self.results_frame, item)

    def _create_object_card(self, parent, item):
        card = tk.Frame(parent, bg=COLORS["bg_primary"], highlightbackground=COLORS["border"], highlightthickness=1, padx=12, pady=12)
        card.pack(fill=tk.X, pady=(0, 10))

        icon_lbl = tk.Label(card, text=item["icon"], font=("Helvetica", 22), bg=COLORS["bg_primary"])
        icon_lbl.pack(side=tk.LEFT, padx=(0, 16))

        info = tk.Frame(card, bg=COLORS["bg_primary"])
        info.pack(side=tk.LEFT, fill=tk.X, expand=True)

        name_lbl = tk.Label(info, text=item["name"], font=FONTS["subtitle"], bg=COLORS["bg_primary"], fg=COLORS["text_primary"], anchor="w")
        name_lbl.pack(fill=tk.X)
        type_lbl = tk.Label(info, text=item["type"], font=FONTS["small"], bg=COLORS["bg_primary"], fg=COLORS["text_muted"], anchor="w")
        type_lbl.pack(fill=tk.X)

        details_lbl = tk.Label(card, text=item["details"], font=FONTS["body"], bg=COLORS["bg_primary"], fg=COLORS["text_secondary"])
        details_lbl.pack(side=tk.RIGHT)

        def _on_click(_e):
            if self.widgets.get("on_object_select"):
                self.widgets["on_object_select"](item)
                
        for w in (card, icon_lbl, info, name_lbl, type_lbl, details_lbl):
            w.bind("<Button-1>", _on_click)
            w.config(cursor="hand2")

    def _load_dummy_data(self):
        self.update_display({
            "results": [
                {"icon": "🌕", "name": "Lua", "type": "Satélite Natural", "details": "Fase: Crescente (65%)"},
                {"icon": "🪐", "name": "Saturno", "type": "Planeta", "details": "Constelação: Aquário"},
                {"icon": "✨", "name": "Sirius", "type": "Estrela dupla", "details": "Mag: -1.46"},
                {"icon": "🌌", "name": "Nebulosa de Órion", "type": "Céu Profundo (M42)", "details": "Mag: 4.0"}
            ]
        })