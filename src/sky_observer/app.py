from sky_observer.ui.main_window import MainWindow


class App:
  main_window: MainWindow

  def __init__(self):
    self.main_window = MainWindow()

  def run(self):
    self.main_window.root.mainloop()
