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

    def bind_events(self, on_add_click, on_select_click=None, on_delete_click=None):
        """
        Conecta os botões de adicionar, selecionar e apagar local ao controlador (MainWindow).
        """
        self.on_add_click = on_add_click
        self.on_select_click = on_select_click
        self.on_delete_click = on_delete_click
        if "btn_add" in self.widgets:
            self.widgets["btn_add"].bind("<Button-1>", lambda _e: self.on_add_click())

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
        
        lat = item.get("latitude", 0.0)
        lon = item.get("longitude", 0.0)
        details_text = f"Lat: {lat:.4f}  ·  Lon: {lon:.4f}"
        tk.Label(info, text=details_text, font=FONTS["small"], bg=COLORS["bg_primary"], fg=COLORS["text_secondary"], anchor="w").pack(fill=tk.X)

        actions = tk.Frame(card, bg=COLORS["bg_primary"])
        actions.pack(side=tk.RIGHT, fill=tk.Y)

        is_active = item.get("active", False)
        
        if is_active:
            # Badge de Selecionado
            badge = tk.Label(
                actions,
                text="⭐ Selecionado",
                font=FONTS["small"],
                bg=COLORS["green_bg"],
                fg=COLORS["green_text"],
                padx=12,
                pady=6
            )
            badge.pack(side=tk.LEFT, padx=(0, 8))
        else:
            # Botão de Selecionar
            btn_select = tk.Label(
                actions,
                text="Selecionar",
                font=FONTS["small"],
                bg=COLORS["bg_secondary"],
                fg=COLORS["text_secondary"],
                padx=12,
                pady=6,
                cursor="hand2"
            )
            btn_select.pack(side=tk.LEFT, padx=(0, 8))
            
            # Hover effect para o botão Selecionar
            def on_enter_select(_e, b=btn_select):
                b.configure(bg=COLORS["blue_bg"], fg=COLORS["blue"])
            def on_leave_select(_e, b=btn_select):
                b.configure(bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"])
            
            btn_select.bind("<Enter>", on_enter_select)
            btn_select.bind("<Leave>", on_leave_select)
            
            # Clique
            if hasattr(self, "on_select_click") and self.on_select_click:
                btn_select.bind("<Button-1>", lambda _e, i_id=item["id"]: self.on_select_click(i_id))

        # Botão de Excluir
        btn_delete = tk.Label(
            actions,
            text="🗑️ Excluir",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_muted"],
            padx=12,
            pady=6,
            cursor="hand2"
        )
        btn_delete.pack(side=tk.LEFT)
        
        # Hover effect para o botão Excluir
        def on_enter_delete(_e, b=btn_delete):
            b.configure(bg=COLORS["red_bg"], fg=COLORS["red_text"])
        def on_leave_delete(_e, b=btn_delete):
            b.configure(bg=COLORS["bg_secondary"], fg=COLORS["text_muted"])
            
        btn_delete.bind("<Enter>", on_enter_delete)
        btn_delete.bind("<Leave>", on_leave_delete)
        
        # Clique
        if hasattr(self, "on_delete_click") and self.on_delete_click:
            btn_delete.bind("<Button-1>", lambda _e, i_id=item["id"]: self.on_delete_click(i_id))

    def _load_dummy_data(self):
        self.update_display({
            "locations": [
                {"name": "Teresina, PI", "details": "Lat: -5.0892  ·  Lon: -42.8019  ·  Brasil", "active": True},
                {"name": "São Paulo, SP", "details": "Lat: -23.5505  ·  Lon: -46.6333  ·  Brasil", "active": False},
            ]
        })