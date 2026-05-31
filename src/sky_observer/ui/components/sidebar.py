import tkinter as tk
from sky_observer.ui.theme import COLORS, FONTS


class Sidebar(tk.Frame):
    """
    Barra lateral esquerda com logo e navegação.
    """

    def __init__(self, parent, on_navigate, on_settings=None):
        """
        parent      = o frame pai (main_window)
        on_navigate = função chamada quando o usuário clica num item de menu
        """
        super().__init__(
            parent,
            bg=COLORS["bg_sidebar"],
            width=190,
        )
        # Impede que o frame encolha automaticamente
        self.pack_propagate(False)

        self.on_navigate = on_navigate
        self.on_settings = on_settings
        self.active_page = "conditions"
        self.nav_buttons = {}

        self._build()

    def _build(self):
        self._create_logo()
        self._create_nav()
        self._create_footer()

    # ── Logo ──────────────────────────────────────────────
    def _create_logo(self):
        logo_frame = tk.Frame(self, bg=COLORS["bg_sidebar"])
        logo_frame.pack(fill=tk.X, padx=16, pady=(18, 14))

        tk.Label(
            logo_frame,
            text="🔭  Sky Observer",
            font=FONTS["logo"],
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_primary"],
            anchor="w",
        ).pack(fill=tk.X)

        tk.Label(
            logo_frame,
            text="v0.1.0 — RAD Python",
            font=FONTS["small"],
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_muted"],
            anchor="w",
        ).pack(fill=tk.X)

        # Linha separadora abaixo do logo
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill=tk.X)

    # ── Navegação ─────────────────────────────────────────
    def _create_nav(self):
        nav_frame = tk.Frame(self, bg=COLORS["bg_sidebar"])
        nav_frame.pack(fill=tk.X, pady=10)

        # Lista de itens: (identificador, ícone, texto do menu)
        items = [
            ("conditions", "📡", "Condições"),
            ("objects",    "🪐", "Objetos"),
            ("locations",  "📍", "Locais"),
        ]

        for page_id, icon, label in items:
            btn = self._nav_button(nav_frame, page_id, icon, label)
            self.nav_buttons[page_id] = btn

        # Deixa o botão inicial como ativo
        self.set_active("conditions")

    def _nav_button(self, parent, page_id, icon, label):
        """Cria um botão de navegação."""
        btn = tk.Label(
            parent,
            text=f"  {icon}  {label}",
            font=FONTS["subtitle"],
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_secondary"],
            anchor="w",
            padx=8,
            pady=9,
            cursor="hand2",
        )
        btn.pack(fill=tk.X, padx=8, pady=1)

        # Quando clicar, muda a página ativa
        btn.bind("<Button-1>", lambda e, p=page_id: self._on_click(p))
        btn.bind("<Enter>", lambda e, b=btn: self._on_hover(b, True))
        btn.bind("<Leave>", lambda e, b=btn, p=page_id: self._on_hover(b, False, p))

        return btn

    def _on_click(self, page_id):
        self.set_active(page_id)
        self.on_navigate(page_id)

    def _on_hover(self, btn, entering, page_id=None):
        # Não muda o botão que já está ativo
        if page_id == self.active_page:
            return
        if entering:
            btn.config(bg=COLORS["bg_primary"], fg=COLORS["text_primary"])
        else:
            btn.config(bg=COLORS["bg_sidebar"], fg=COLORS["text_secondary"])

    def set_active(self, page_id):
        # Remove o estilo ativo do botão anterior
        if self.active_page in self.nav_buttons:
            old = self.nav_buttons[self.active_page]
            old.config(bg=COLORS["bg_sidebar"], fg=COLORS["text_secondary"])

        self.active_page = page_id

        # Aplica o estilo ativo no novo botão, se for um item principal de navegação
        if page_id in self.nav_buttons:
            new = self.nav_buttons[page_id]
            new.config(bg=COLORS["blue_bg"], fg=COLORS["blue"])

    # ── Rodapé ────────────────────────────────────────────
    def _create_footer(self):
        # Empurra o botão de configurações para o final
        tk.Frame(self, bg=COLORS["bg_sidebar"]).pack(fill=tk.BOTH, expand=True)

        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill=tk.X)

        settings_btn = tk.Label(
            self,
            text="  ⚙️  Configurações",
            font=FONTS["body"],
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_secondary"],
            anchor="w",
            padx=8,
            pady=10,
            cursor="hand2",
        )
        settings_btn.pack(fill=tk.X, padx=8, pady=6)
        
        settings_btn.bind("<Button-1>", self._on_settings_click)

    def _on_settings_click(self, _event):
        # Resolve de forma segura a chamada do callback para evitar
        # problemas de referência 'None' em tempo de execução no Tkinter.
        self.set_active("settings")
        
        on_settings = self.on_settings
        if on_settings:
            on_settings()