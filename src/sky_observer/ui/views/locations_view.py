import tkinter as tk
from sky_observer.ui.theme import COLORS, FONTS


class LocationsView(tk.Frame):
    """
    Tela para gerenciamento de locais favoritos.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_primary"])
        # Dicionário para armazenar elementos interativos
        self.widgets = {}
        self._build()
        self._load_dummy_data()

    def _build(self):
        self._create_topbar()
        self._create_add_location_area()
        self._create_list_area()

    # ── Topbar ────────────────────────────────────────────
    def _create_topbar(self):
        bar = tk.Frame(self, bg=COLORS["bg_primary"], pady=12)
        bar.pack(fill=tk.X, padx=20)

        tk.Label(
            bar,
            text="Locais Favoritos",
            font=FONTS["title"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
        ).pack(side=tk.LEFT)

        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill=tk.X)

    # ── Área de Adicionar ─────────────────────────────────
    def _create_add_location_area(self):
        add_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=16)
        add_frame.pack(fill=tk.X, padx=20)

        btn_add = tk.Label(
            add_frame,
            text="➕  Adicionar novo local",
            font=FONTS["small"],
            bg=COLORS["blue_bg"],
            fg=COLORS["blue"],
            padx=16,
            pady=8,
            cursor="hand2"
        )
        btn_add.pack(side=tk.LEFT)
        self.widgets["btn_add"] = btn_add

    def bind_events(self, on_add_click):
        """
        Conecta o botão de adicionar local ao controlador (MainWindow).
        Permite delegar a abertura de um modal ou busca para a classe principal.
        """
        if "btn_add" in self.widgets:
            self.widgets["btn_add"].bind("<Button-1>", lambda _e: on_add_click())

    # ── Lista de Locais ───────────────────────────────────
    def _create_list_area(self):
        self.list_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=20)

    def update_display(self, data: dict):
        """
        Atualiza a lista visual de locais favoritos.
        Destrói os widgets antigos e constrói novos com base no dicionário recebido.
        """
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for item in data.get("locations", []):
            self._create_location_card(self.list_frame, item)

    def _create_location_card(self, parent, item):
        card = tk.Frame(parent, bg=COLORS["bg_primary"], highlightbackground=COLORS["border"], highlightthickness=1, padx=16, pady=12)
        card.pack(fill=tk.X, pady=(0, 10))

        info = tk.Frame(card, bg=COLORS["bg_primary"])
        info.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(info, text=item["name"], font=FONTS["subtitle"], bg=COLORS["bg_primary"], fg=COLORS["text_primary"], anchor="w").pack(fill=tk.X)
        tk.Label(info, text=item["details"], font=FONTS["small"], bg=COLORS["bg_primary"], fg=COLORS["text_secondary"], anchor="w").pack(fill=tk.X)

        is_active = item.get("active", False)
        btn_text = "⭐ Selecionado" if is_active else "Selecionar"
        
        tk.Label(card, text=btn_text, font=FONTS["small"], bg=COLORS["green_bg"] if is_active else COLORS["bg_secondary"], fg=COLORS["green_text"] if is_active else COLORS["text_secondary"], padx=12, pady=6, cursor="hand2" if not is_active else "arrow").pack(side=tk.RIGHT)

    def _load_dummy_data(self):
        self.update_display({
            "locations": [
                {"name": "Teresina, PI", "details": "Lat: -5.0892  ·  Lon: -42.8019  ·  Brasil", "active": True},
                {"name": "São Paulo, SP", "details": "Lat: -23.5505  ·  Lon: -46.6333  ·  Brasil", "active": False},
            ]
        })