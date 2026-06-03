import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
from typing import final
from sky_observer.ui.theme import COLORS, toggle_theme
from sky_observer.ui.components.sidebar import Sidebar
from sky_observer.ui.views.conditions_view import ConditionsView
from sky_observer.ui.views.objects_view import ObjectsView
from sky_observer.ui.views.locations_view import LocationsView
from sky_observer.ui.views.settings_view import SettingsView
from sky_observer.db.connection import get_connection
from sky_observer.db.location_service import LocationService
from sky_observer.infra.openmeteo.client import OpenMeteoClient
from sky_observer.infra.skyfield.client import SkyFieldClient


@final
class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sky Observer")
        self.root.geometry("900x620")
        self.root.minsize(750, 500)
        self.root.configure(bg=COLORS["bg_primary"])

        # Mostra uma tela de carregamento (Splash Screen) inicial
        self.loading_frame = tk.Frame(self.root, bg=COLORS["bg_primary"])
        self.loading_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            self.loading_frame,
            text="🔭",
            font=("Helvetica", 48),
            bg=COLORS["bg_primary"]
        ).pack(expand=True, side=tk.TOP, pady=(120, 10))
        
        tk.Label(
            self.loading_frame,
            text="Iniciando Sky Observer...",
            font=("Helvetica", 16, "bold"),
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.TOP)
        
        tk.Label(
            self.loading_frame,
            text="Sincronizando catálogos astronômicos (isso pode demorar na primeira vez)...",
            font=("Helvetica", 10),
            bg=COLORS["bg_primary"],
            fg=COLORS["text_secondary"]
        ).pack(side=tk.TOP, pady=(5, 120))

        # Agenda a inicialização pesada para 100ms depois, permitindo que a tela de loading apareça
        self.root.after(100, self._initialize_heavy_components)

    def _initialize_heavy_components(self):
        self.db_conn = get_connection()
        self.location_service = LocationService()

        # Inicializa clientes de API e gerência de estado (Aqui ocorre o download do .bsp)
        self.weather_client = OpenMeteoClient()
        self.skyfield_client = SkyFieldClient(0.0, 0.0)
        self.current_location = None

        # Destrói a tela de carregamento e monta a interface principal
        self.loading_frame.destroy()
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
            
        # Dispara carregamento dinâmico ao abrir a tela de locais
        if page == "locations":
            self._load_locations()

    def _load_locations(self):
        """Busca os locais no banco e injeta na LocationsView."""
        locs = self.location_service.list()
        data = {
            "locations": [{"id": l.id, "name": l.name, "latitude": l.latitude, "longitude": l.longitude} for l in locs]
        }
        if "locations" in self.frames:
            self.frames["locations"].update_display(data)

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
        """Abre um menu suspenso com as cidades salvas no banco."""
        locs = self.location_service.list()
        if not locs:
            messagebox.showinfo("Localização", "Nenhum local salvo. Adicione cidades na aba 'Locais'.")
            return
        
        menu = tk.Menu(self.root, tearoff=0)
        for loc in locs:
            menu.add_command(label=loc.name, command=lambda l=loc: self._set_current_location(l))
        
        # Exibe o menu na exata posição em que o mouse clicou
        x, y = self.root.winfo_pointerxy()
        menu.tk_popup(x, y)

    def _set_current_location(self, loc):
        """Atualiza o estado atual com a localização escolhida pelo usuário."""
        self.current_location = loc
        # Força a atualização automática dos dados climáticos para a nova cidade
        self._update_conditions_data()

    def _update_conditions_data(self):
        """Busca e atualiza os dados climáticos e astronômicos para a cidade atual."""
        
        if not self.current_location:
            messagebox.showwarning("Aviso", "Selecione um local em '📍 Selecione um local' primeiro.")
            return
            
        self.root.update_idletasks() # Dá um fôlego para a tela mostrar o carregamento
        
        # 1. Busca Clima
        weather = self.weather_client.get_weather(self.current_location.latitude, self.current_location.longitude)
        if not weather:
            messagebox.showerror("Erro", "Não foi possível obter dados do clima para esta cidade.")
            return
            
        score = 100 - int(weather.cloud_cover_pct)
        status_color = "good" if score >= 70 else ("fair" if score >= 40 else "bad")
        
        # 2. Busca Planetas com Skyfield
        planets_data = []
        for p in ["Marte", "Júpiter", "Saturno", "Vênus"]:
            obj = self.skyfield_client.search_object(p, self.current_location.latitude, self.current_location.longitude)
            if obj:
                planets_data.append({
                    "name": p,
                    "detail": f"Alt. {obj.altitude:.0f}° · Az. {obj.azimuth:.0f}°",
                    "status": "green" if obj.visible else "red"
                })
                
        # 3. Formata e envia para a View
        ui_data = {
            "is_object_context": False,
            "location": self.current_location.name,
            "score": score,
            "status": status_color,
            "title": "Boas condições" if status_color == "good" else "Condições desfavoráveis",
            "subtitle": weather.weather_description,
            "metrics": {
                "cloud_cover": f"{int(weather.cloud_cover_pct)}",
                "seeing": "7",
                "humidity": f"{int(weather.humidity_pct)}",
                "moon_phase": "N/A",
            },
            "planets": planets_data
        }
        self.frames["conditions"].update_display(ui_data)

    def _on_search_objects(self, query):
        """Ação disparada ao clicar no botão buscar na tela de Objetos."""
        if not query.strip():
            messagebox.showwarning("Aviso", "Por favor, digite o nome de um objeto.")
            return

        if not self.current_location:
            messagebox.showwarning("Aviso", "Selecione um local na aba Condições primeiro.")
            return
            
        self.root.update_idletasks()
        
        query_formatada = query.strip().capitalize()
        obj = self.skyfield_client.search_object(query_formatada, self.current_location.latitude, self.current_location.longitude)
        
        if obj:
            data = {
                "results": [
                    {
                        "icon": "🔭",
                        "name": query_formatada,
                        "type": "Objeto Celeste",
                        "details": f"Alt: {obj.altitude:.1f}° | Visível: {'Sim' if obj.visible else 'Não'}"
                    }
                ]
            }
            self.frames["objects"].update_display(data)
        else:
            messagebox.showinfo("Busca", f"Objeto '{query}' não encotrado nos catálogos.")

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
        """Abre prompt de busca, consulta a API e salva no banco de dados."""
        query = simpledialog.askstring("Adicionar Local", "Digite o nome da cidade (ex: São Paulo):")
        if not query or not query.strip():
            return
            
        self.root.update_idletasks() # Força a tela a não congelar caso a internet demore
        
        result = self.weather_client.search_location(query.strip())
        if result:
            self.location_service.register(
                name=result.name,
                latitude=result.latitude,
                longitude=result.longitude
            )
            messagebox.showinfo("Sucesso", f"Local '{result.name}' ({result.country}) salvo com sucesso!")
            
            if self.sidebar.active_page == "locations":
                self._load_locations()
        else:
            messagebox.showerror("Erro", f"Não foi possível encontrar a cidade '{query}'.")

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