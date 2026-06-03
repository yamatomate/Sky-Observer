import queue
import threading
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
from typing import final

from sky_observer.db.location_service import LocationService
from sky_observer.services.observation_service import ObservationService
from sky_observer.ui.components.sidebar import Sidebar
from sky_observer.ui.theme import COLORS, toggle_theme
from sky_observer.ui.views.conditions_view import ConditionsView
from sky_observer.ui.views.locations_view import LocationsView
from sky_observer.ui.views.objects_view import ObjectsView
from sky_observer.ui.views.settings_view import SettingsView

observation_service: ObservationService | None = None


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
      self.loading_frame, text="🔭", font=("Helvetica", 48), bg=COLORS["bg_primary"]
    ).pack(expand=True, side=tk.TOP, pady=(120, 10))

    tk.Label(
      self.loading_frame,
      text="Iniciando Sky Observer...",
      font=("Helvetica", 16, "bold"),
      bg=COLORS["bg_primary"],
      fg=COLORS["text_primary"],
    ).pack(side=tk.TOP)

    tk.Label(
      self.loading_frame,
      text="Sincronizando catálogos astronômicos (isso pode demorar na primeira vez)...",
      font=("Helvetica", 10),
      bg=COLORS["bg_primary"],
      fg=COLORS["text_secondary"],
    ).pack(side=tk.TOP, pady=(5, 120))

    # Agenda a inicialização pesada para 100ms depois, permitindo que a tela de loading apareça
    self.root.after(100, self._initialize_heavy_components)

  def _initialize_heavy_components(self):
    # LocationService para CRUD de locais (list/register) — não exposto no ObservationService
    self.location_service = LocationService()
    self.current_location = None

    # Fila de tarefas para o worker thread dedicado
    self._task_queue = queue.Queue()

    # Worker thread dedicado: cria e possui o ObservationService.
    # Isso evita problemas de SQLite thread-safety do niquests_cache,
    # pois todas as chamadas de rede ocorrem sempre na mesma thread.
    self._worker = threading.Thread(target=self._worker_loop, daemon=True)
    self._worker.start()

    # Destrói a tela de carregamento e monta a interface principal
    self.loading_frame.destroy()
    self._setup_ui()

  def _worker_loop(self):
    """Loop do worker thread dedicado. Cria o ObservationService nesta thread
    para que o SQLite do niquests_cache seja acessado sempre da mesma thread."""
    global observation_service
    observation_service = ObservationService()
    while True:
      task = self._task_queue.get()
      if task is None:
        break
      try:
        task()
      except Exception:
        pass  # Erros já são tratados dentro de cada task

  def _run_in_worker(self, task_fn):
    """Despacha uma tarefa para o worker thread."""
    self._task_queue.put(task_fn)

  def _setup_ui(self):
    # Frame principal divide a tela em sidebar + conteúdo
    self.main_frame = tk.Frame(self.root, bg=COLORS["bg_primary"])
    self.main_frame.pack(fill=tk.BOTH, expand=True)

    # Sidebar à esquerda
    self.sidebar = Sidebar(
      self.main_frame, on_navigate=self._navigate, on_settings=self._on_settings_click
    )
    self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

    # Linha divisória entre sidebar e conteúdo
    tk.Frame(self.main_frame, bg=COLORS["border"], width=1).pack(
      side=tk.LEFT, fill=tk.Y
    )

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
      on_location_click=self._on_location_click, on_back_click=self._on_conditions_back
    )
    self.frames["conditions"] = cond_view

    obj_view = ObjectsView(self.content_area)
    obj_view.bind_events(
      on_search=self._on_search_objects, on_object_select=self._on_object_select
    )
    self.frames["objects"] = obj_view

    loc_view = LocationsView(self.content_area)
    loc_view.bind_events(on_add_click=self._on_add_location)
    self.frames["locations"] = loc_view

    set_view = SettingsView(self.content_area)
    set_view.bind_events(
      on_clear_cache=self._on_clear_cache,
      on_toggle_setting=self._on_toggle_setting,
      on_toggle_theme=self._on_toggle_theme,
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
      "locations": [
        {"id": loc.id, "name": loc.name, "latitude": loc.latitude, "longitude": loc.longitude}
        for loc in locs
      ]
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
      messagebox.showinfo(
        "Localização", "Nenhum local salvo. Adicione cidades na aba 'Locais'."
      )
      return

    menu = tk.Menu(self.root, tearoff=0)
    for loc in locs:
      menu.add_command(
        label=loc.name, command=lambda loc=loc: self._set_current_location(loc)
      )

    # Exibe o menu na exata posição em que o mouse clicou
    x, y = self.root.winfo_pointerxy()
    menu.tk_popup(x, y)

  def _set_current_location(self, loc):
    """Atualiza o estado atual com a localização escolhida pelo usuário."""
    self.current_location = loc
    # Força a atualização automática dos dados climáticos para a nova cidade
    self._update_conditions_data()

  def _update_conditions_data(self):
    """Busca e atualiza os dados climáticos e astronômicos para a cidade atual via ObservationService."""

    if not self.current_location:
      messagebox.showwarning(
        "Aviso", "Selecione um local em '📍 Selecione um local' primeiro."
      )
      return

    # Captura os valores AGORA para evitar que o worker leia dados obsoletos
    lat = self.current_location.latitude
    lon = self.current_location.longitude
    name = self.current_location.name

    # Feedback visual de carregamento imediato
    self.frames["conditions"].update_display(
      {
        "title": "Carregando dados...",
        "subtitle": "Consultando clima e efemérides...",
      }
    )

    def run_query(lat=lat, lon=lon, name=name):
      try:
        assert observation_service is not None
        result = observation_service.get_conditions(lat, lon, name)

        ui_data = {
          "is_object_context": False,
          "location": result.location,
          "score": result.score,
          "status": result.status,
          "title": result.title,
          "subtitle": result.subtitle,
          "metrics": {
            "cloud_cover": result.metrics.cloud_cover,
            "seeing": result.metrics.seeing,
            "humidity": result.metrics.humidity,
            "moon_phase": result.metrics.moon_phase,
          },
          "planets": [
            {"name": p.name, "detail": p.detail, "status": p.status}
            for p in result.planets
          ],
        }
        self.root.after(0, lambda: self.frames["conditions"].update_display(ui_data))

      except Exception as e:
        err_msg = str(e)
        self.root.after(
          0,
          lambda: messagebox.showerror(
            "Erro", f"Falha ao carregar condições: {err_msg}"
          ),
        )

    self._run_in_worker(run_query)

  def _on_search_objects(self, query):
    """Ação disparada ao clicar no botão buscar na tela de Objetos."""
    if not query.strip():
      messagebox.showwarning("Aviso", "Por favor, digite o nome de um objeto.")
      return

    if not self.current_location:
      messagebox.showwarning("Aviso", "Selecione um local na aba Condições primeiro.")
      return

    query_formatada = query.strip().capitalize()

    # Captura os valores AGORA para evitar que o worker leia dados obsoletos
    lat = self.current_location.latitude
    lon = self.current_location.longitude

    def run_search(lat=lat, lon=lon, query_formatada=query_formatada):
      try:
        assert observation_service is not None
        all_objects = observation_service.get_visible_objects(lat, lon, horario=None)

        matched = [
          obj for obj in all_objects if query_formatada.lower() in obj.name.lower()
        ]

        if matched:
          icon_map = {
            "Lua": "🌕",
            "Mercúrio": "☿️",
            "Vênus": "♀️",
            "Marte": "♂️",
            "Júpiter": "♃",
            "Saturno": "🪐",
            "Urano": "⛢",
            "Netuno": "♆",
          }
          data = {
            "results": [
              {
                "icon": icon_map.get(obj.name, "🔭"),
                "name": obj.name,
                "type": "Objeto Celeste",
                "details": f"{obj.details} | Visível: {'Sim' if obj.status == 'green' else 'Não'}",
              }
              for obj in matched
            ]
          }
          self.root.after(0, lambda: self.frames["objects"].update_display(data))
        else:
          self.root.after(
            0,
            lambda: messagebox.showinfo(
              "Busca", f"Objeto '{query_formatada}' não encontrado nos catálogos."
            ),
          )

      except Exception as e:
        err_msg = str(e)
        self.root.after(
          0, lambda: messagebox.showerror("Erro", f"Falha na busca: {err_msg}")
        )

    self._run_in_worker(run_search)

  def _on_object_select(self, item):
    """Ação ao clicar em um objeto na lista de busca."""
    # Muda a navegação visual para 'conditions'
    self.sidebar.set_active("conditions")
    self._navigate("conditions")

    if not self.current_location:
      messagebox.showwarning("Aviso", "Selecione um local primeiro.")
      return

    # Captura os valores AGORA para evitar que o worker leia dados obsoletos
    lat = self.current_location.latitude
    lon = self.current_location.longitude
    name = self.current_location.name

    # Feedback visual imediato
    self.frames["conditions"].update_display(
      {
        "is_object_context": True,
        "title": f"Carregando: {item['name']}...",
        "subtitle": "Consultando condições para este objeto...",
      }
    )

    def run_query(lat=lat, lon=lon, name=name, item=item):
      try:
        assert observation_service is not None
        result = observation_service.get_conditions(lat, lon, name)

        selected_planet = [p for p in result.planets if p.name == item["name"]]

        ui_data = {
          "is_object_context": True,
          "location": result.location,
          "score": result.score,
          "status": result.status,
          "title": f"Observando: {item['name']}",
          "subtitle": f"{item['type']} — {item['details']}",
          "metrics": {
            "cloud_cover": result.metrics.cloud_cover,
            "seeing": result.metrics.seeing,
            "humidity": result.metrics.humidity,
            "moon_phase": result.metrics.moon_phase,
          },
          "planets": [
            {"name": p.name, "detail": p.detail, "status": p.status}
            for p in (selected_planet if selected_planet else result.planets)
          ],
        }
        self.root.after(0, lambda: self.frames["conditions"].update_display(ui_data))

      except Exception as e:
        err_msg = str(e)
        self.root.after(
          0, lambda: messagebox.showerror("Erro", f"Falha ao carregar dados: {err_msg}")
        )

    self._run_in_worker(run_query)

  def _on_conditions_back(self):
    """Ação ao clicar no botão voltar na tela de condições (quando olhando um objeto)."""
    # Restaura a visão geral com dados reais em vez de dummy data
    self._update_conditions_data()
    self.sidebar.set_active("objects")
    self._navigate("objects")

  def _on_add_location(self):
    """Abre prompt de busca, consulta o ObservationService e salva no banco de dados."""
    query = simpledialog.askstring(
      "Adicionar Local", "Digite o nome da cidade (ex: São Paulo):"
    )
    if not query or not query.strip():
      return

    search_term = query.strip()

    def run_add(term=search_term):
      try:
        assert observation_service is not None
        result = observation_service.search_location(term)
        if result:
          # Devolve a escrita no banco para a thread principal (evita SQLite cross-thread)
          loc_name = result.name
          loc_lat = result.latitude
          loc_lon = result.longitude
          loc_country = result.country

          def do_register(name=loc_name, lat=loc_lat, lon=loc_lon, country=loc_country):
            self.location_service.register(
              name=name,
              latitude=lat,
              longitude=lon,
            )
            messagebox.showinfo(
              "Sucesso", f"Local '{name}' ({country}) salvo com sucesso!"
            )
            # Atualiza a lista de locais se estiver na aba
            if self.sidebar.active_page == "locations":
              self._load_locations()

          self.root.after(0, do_register)
        else:
          self.root.after(
            0,
            lambda: messagebox.showerror(
              "Erro", f"Não foi possível encontrar a cidade '{term}'."
            ),
          )
      except Exception as e:
        err_msg = str(e)
        self.root.after(
          0,
          lambda: messagebox.showerror("Erro", f"Falha ao adicionar local: {err_msg}"),
        )

    self._run_in_worker(run_add)

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

    # Recarrega os dados nas views reconstruídas
    if self.current_location:
      self._update_conditions_data()
    self._load_locations()

  def _on_clear_cache(self):
    messagebox.showinfo(
      "Configurações", "Em breve: Limpeza do banco de dados de cache local (niquests)."
    )

  def _on_toggle_setting(self, setting_key):
    messagebox.showinfo(
      "Configurações", f"Em breve: Alternar preferência '{setting_key}'."
    )
