import tkinter as tk
import tkinter.messagebox as messagebox
from typing import final
from sky_observer.ui.theme import COLORS, toggle_theme
from sky_observer.ui.components.sidebar import Sidebar
from sky_observer.ui.views.conditions_view import ConditionsView
from sky_observer.ui.views.objects_view import ObjectsView
from sky_observer.ui.views.locations_view import LocationsView
from sky_observer.ui.views.settings_view import SettingsView


@final
class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sky Observer")
        self.root.geometry("900x620")
        self.root.minsize(750, 500)
        self.root.configure(bg=COLORS["bg_primary"])

        self._setup_ui()

    def _setup_ui(self):
        # Frame principal divide a tela em sidebar + conteúdo
        self.main_frame = tk.Frame(self.root, bg=COLORS["bg_primary"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar à esquerda
        self.sidebar = Sidebar(
            self.main_frame,
            on_navigate=self._navigate,
            on_settings=self._on_settings_click
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Linha divisória entre sidebar e conteúdo
        tk.Frame(self.main_frame, bg=COLORS["border"], width=1).pack(side=tk.LEFT, fill=tk.Y)

        # Área de conteúdo à direita
        self.content_area = tk.Frame(self.main_frame, bg=COLORS["bg_primary"])
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        self._init_frames()
        self._navigate("conditions")

    def _init_frames(self):
        """
        Inicializa todas as telas (views) uma única vez e as empilha na mesma célula do grid.
        Isso evita destruir e recriar os widgets, preservando o estado e melhorando a performance.
        """
        self.frames = {}

        # Prepara todas as telas e injeta as funções de resposta (callbacks)
        cond_view = ConditionsView(self.content_area)
        cond_view.bind_events(
            on_location_click=self._on_location_click,
            on_date_click=self._on_date_click,
            on_back_click=self._on_conditions_back
        )
        self.frames["conditions"] = cond_view
        
        obj_view = ObjectsView(self.content_area)
        obj_view.bind_events(
            on_search=self._on_search_objects,
            on_object_select=self._on_object_select
        )
        self.frames["objects"] = obj_view
        
        loc_view = LocationsView(self.content_area)
        loc_view.bind_events(on_add_click=self._on_add_location)
        self.frames["locations"] = loc_view

        set_view = SettingsView(self.content_area)
        set_view.bind_events(
            on_clear_cache=self._on_clear_cache,
            on_toggle_setting=self._on_toggle_setting,
            on_toggle_theme=self._on_toggle_theme
        )
        self.frames["settings"] = set_view

        # Posiciona todas na mesma célula (row=0, column=0) para sobreposição
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

    def _navigate(self, page):
        """
        Traz a tela solicitada para o topo (frente).
        Como todas usam grid(row=0, column=0), o tkraise() faz com que
        a tela desejada cubra as outras.
        """
        frame = self.frames.get(page)
        if frame:
            frame.tkraise()

    def _create_placeholder_frame(self, title, subtitle):
        """Tela temporária para páginas ainda não implementadas."""
        frame = tk.Frame(self.content_area, bg=COLORS["bg_primary"])

        tk.Label(
            frame,
            text=title,
            font=("Helvetica", 18, "bold"),
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
        ).pack(expand=True)

        tk.Label(
            frame,
            text=subtitle,
            font=("Helvetica", 12),
            bg=COLORS["bg_primary"],
            fg=COLORS["text_secondary"],
        ).pack()
        
        return frame

    # ── Controladores de Eventos (Event Handlers) ──────────
    # Aqui é onde a equipe de backend deve integrar as chamadas da API (OpenMeteo, Skyfield, etc).
    def _on_settings_click(self):
        """Ação ao clicar na aba inferior de Configurações."""
        self._navigate("settings")

    def _on_location_click(self):
        messagebox.showinfo("Localização", "Em breve: Busca de cidades (Integração com OpenMeteo API).")

    def _on_date_click(self, date_type):
        """Ação ao alternar entre Hoje e Amanhã."""
        # Atualiza a UI para mostrar qual botão está ativo
        self.frames["conditions"].set_active_date(date_type)
        # TODO (Backend): Buscar dados para 'today' ou 'tomorrow' e chamar self.frames["conditions"].update_display(data)

    def _on_search_objects(self, query):
        """Ação disparada ao clicar no botão buscar na tela de Objetos."""
        if not query.strip():
            messagebox.showwarning("Aviso", "Por favor, digite o nome de um objeto.")
            return
            
        # TODO (Backend): Integrar com Skyfield para buscar o objeto 'query' e repassar para a View
        messagebox.showinfo("Busca de Objetos", f"Em breve integrando Skyfield para buscar: '{query}'")

    def _on_object_select(self, item):
        """Ação ao clicar em um objeto na lista de busca."""
        # Muda a navegação visual para 'conditions'
        self.sidebar.set_active("conditions")
        self._navigate("conditions")
        
        # Injeta dados fictícios direcionados ao objeto clicado
        status_color = "good" if item["name"] in ["Lua", "Júpiter", "Saturno"] else "fair"
        mock_data = {
            "is_object_context": True,
            "location": "Teresina, PI",
            "score": 95 if status_color == "good" else 65,
            "status": status_color,
            "title": f"Observando: {item['name']}",
            "subtitle": f"{item['type']} — {item['details']}",
            "metrics": {
                "cloud_cover": "5",
                "seeing": "8",
                "humidity": "42",
                "moon_phase": "65",
            },
            "planets": [
                {"name": item["name"], "detail": "Foco ajustado para este objeto.", "status": "green" if status_color == "good" else "yellow"}
            ]
        }
        self.frames["conditions"].update_display(mock_data)

    def _on_conditions_back(self):
        """Ação ao clicar no botão voltar na tela de condições (quando olhando um objeto)."""
        self.frames["conditions"]._load_dummy_data() # Restaura visão geral mockada
        self.sidebar.set_active("objects")
        self._navigate("objects")

    def _on_add_location(self):
        messagebox.showinfo("Locais", "Em breve: Buscador de cidades via OpenMeteo.")

    def _on_toggle_theme(self):
        """Altera entre o modo Claro e Escuro reconstruindo a interface de forma rápida."""
        toggle_theme()
        current_page = self.sidebar.active_page
        
        # Atualiza raiz e recria os componentes (Instantâneo)
        self.root.configure(bg=COLORS["bg_primary"])
        self.main_frame.destroy()
        self._setup_ui()
        
        # Restaura a página que estava ativa
        self.sidebar.set_active(current_page)
        self._navigate(current_page)
    def _on_clear_cache(self):
        messagebox.showinfo("Configurações", "Em breve: Limpeza do banco de dados de cache local (niquests).")

    def _on_toggle_setting(self, setting_key):
        messagebox.showinfo("Configurações", f"Em breve: Alternar preferência '{setting_key}'.")