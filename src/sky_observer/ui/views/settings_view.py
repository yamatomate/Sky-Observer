import tkinter as tk
from sky_observer.ui.theme import COLORS, FONTS


class SettingsView(tk.Frame):
    """
    Tela de configurações do sistema.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_primary"])
        self.widgets = {}
        self._build()
        self._load_dummy_data()
        # Inicializa com dados padrão por enquanto
        self.update_display({"temp_unit": "°C", "time_format": "24h"})

    def _build(self):
        self._create_topbar()
        self._create_content()

    # ── Topbar ────────────────────────────────────────────
    def _create_topbar(self):
        bar = tk.Frame(self, bg=COLORS["bg_primary"], pady=12)
        bar.pack(fill=tk.X, padx=20)

        tk.Label(
            bar,
            text="Configurações",
            font=FONTS["title"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
        ).pack(side=tk.LEFT)

        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill=tk.X)

    # ── Conteúdo ──────────────────────────────────────────
    def _create_content(self):
        container = tk.Frame(self, bg=COLORS["bg_primary"])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- Preferências ---
        tk.Label(container, text="Preferências Gerais", font=FONTS["subtitle"], bg=COLORS["bg_primary"], fg=COLORS["text_primary"]).pack(anchor="w", pady=(0, 10))

        self._create_setting_row(container, "Unidade de Temperatura", "temp_unit", "°C")
        self._create_setting_row(container, "Formato de Hora", "time_format", "24h")
        self._create_setting_row(container, "Tema Visual", "theme", "Alternar 🌓")

        tk.Frame(container, bg=COLORS["border"], height=1).pack(fill=tk.X, pady=20)

        # --- Sistema ---
        tk.Label(container, text="Sistema e Dados", font=FONTS["subtitle"], bg=COLORS["bg_primary"], fg=COLORS["text_primary"]).pack(anchor="w", pady=(0, 10))

        btn_clear = tk.Label(container, text="🗑️  Limpar Cache", font=FONTS["small"], bg=COLORS["red_bg"], fg=COLORS["red"], padx=16, pady=8, cursor="hand2")
        btn_clear.pack(anchor="w")
        self.widgets["btn_clear_cache"] = btn_clear

    def _create_setting_row(self, parent, label_text, key, initial_value):
        row = tk.Frame(parent, bg=COLORS["bg_primary"])
        row.pack(fill=tk.X, pady=6)

        tk.Label(row, text=label_text, font=FONTS["body"], bg=COLORS["bg_primary"], fg=COLORS["text_secondary"]).pack(side=tk.LEFT)
        
        val_label = tk.Label(row, text=initial_value, font=FONTS["body"], bg=COLORS["bg_secondary"], fg=COLORS["text_primary"], padx=12, pady=4, cursor="hand2")
        val_label.pack(side=tk.RIGHT)
        self.widgets[f"setting_{key}"] = val_label

    def bind_events(self, on_clear_cache, on_toggle_setting, on_toggle_theme):
        if "btn_clear_cache" in self.widgets:
            self.widgets["btn_clear_cache"].bind("<Button-1>", lambda _e: on_clear_cache())
        if "setting_temp_unit" in self.widgets:
            self.widgets["setting_temp_unit"].bind("<Button-1>", lambda _e: on_toggle_setting("temp_unit"))
        if "setting_time_format" in self.widgets:
            self.widgets["setting_time_format"].bind("<Button-1>", lambda _e: on_toggle_setting("time_format"))
        if "setting_theme" in self.widgets:
            self.widgets["setting_theme"].bind("<Button-1>", lambda _e: on_toggle_theme())

    def update_display(self, data: dict):
        if "temp_unit" in data:
            self.widgets["setting_temp_unit"].config(text=data["temp_unit"])
        if "time_format" in data:
            self.widgets["setting_time_format"].config(text=data["time_format"])

    def _load_dummy_data(self):
        self.update_display({"temp_unit": "°C", "time_format": "24h"})