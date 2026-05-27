import tkinter as tk
from tkinter import ttk
from typing import final


@final
class MainWindow:
  def __init__(self):
    self.root = tk.Tk()
    self.root.title("Sky Observer")
    self.root.geometry("800x600")
    self._setup_ui()

  def _setup_ui(self):
    self._create_header()
    self._create_content_area()

  def _create_header(self):
    header = ttk.Frame(self.root)
    header.pack(fill=tk.X)
    header_label = ttk.Label(header, text="Sky Observer", font=("Helvetica", 16))
    header_label.pack()
    pass

  def _create_content_area(self):
    content = ttk.Frame(self.root)
    content_label = tk.Label(content, text="Haha, testes testes teste.")
    content_label.pack(fill=tk.BOTH, expand=True)
    content.pack(fill=tk.BOTH, expand=True)
    pass
