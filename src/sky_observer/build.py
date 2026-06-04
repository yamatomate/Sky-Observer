"""
build.py — Empacota o Sky Observer com PyInstaller.

Uso:
  uv run python build.py                # Executável único, sem console
  uv run python build.py --console      # Com console (debug)
  uv run python build.py --onedir       # Pasta em vez de .exe único (startup mais rápido)
"""

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "SkyObserver"
ENTRY_POINT = Path("src/sky_observer/main.py")
BSP_FILE = Path("de421.bsp")

HIDDEN_IMPORTS = [
  # Skyfield (carregamento dinâmico do JPL)
  "skyfield",
  "skyfield.api",
  "skyfield.data",
  "skyfield.data.planets",
  "skyfield.sgp4lib",
  "skyfield.timelib",
  "skyfield.framelib",
  "skyfield.positionlib",
  "skyfield.jpllib",
  # Numpy (backends internos em C)
  "numpy",
  "numpy.core._methods",
  "numpy.core._dtype_ctypes",
  # HTTP
  "niquests",
  "urllib3",
  "openmeteo_requests",
  # Nativos do Python (garantir bundling no Windows)
  "sqlite3",
  "_sqlite3",
  "tkinter",
  "_tkinter",
]

EXCLUDES = [
  "pandas",
  "pytest",
  "pytest_sugar",
  "ruff",
  "pyinstaller",
  "pip",
  "setuptools",
  "wheel",
  "unittest",
  "pdb",
]


def find_bsp() -> Path:
  for candidate in [BSP_FILE, Path.home() / ".skyfield" / BSP_FILE.name]:
    if candidate.exists():
      return candidate.resolve()
  
  print(f"📥 '{BSP_FILE.name}' não encontrado. Baixando via Skyfield...")
  try:
    from skyfield.api import load
    load(BSP_FILE.name)
    if BSP_FILE.exists():
      return BSP_FILE.resolve()
  except Exception as e:
    print(f"❌ Falha ao baixar '{BSP_FILE.name}' automaticamente: {e}")

  print(f"❌ '{BSP_FILE.name}' não encontrado. Execute 'uv run start' primeiro.")
  sys.exit(1)


def build(*, console: bool = False, onedir: bool = False):
  bsp = find_bsp()

  # Limpa builds anteriores
  for d in [Path("build"), Path("dist")]:
    if d.exists():
      shutil.rmtree(d, ignore_errors=True)

  sep = ";" if platform.system() == "Windows" else ":"

  cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    str(ENTRY_POINT),
    "--name",
    APP_NAME,
    "--noconfirm",
    "--clean",
    "--onedir" if onedir else "--onefile",
    "--console" if console else "--windowed",
    "--paths",
    "src",
    "--add-data",
    f"{bsp}{sep}.",
    "--distpath",
    "dist",
    "--workpath",
    "build",
  ]

  for imp in HIDDEN_IMPORTS:
    cmd.extend(["--hidden-import", imp])
  for exc in EXCLUDES:
    cmd.extend(["--exclude-module", exc])

  mode = "onedir" if onedir else "onefile"
  win = "console" if console else "windowed"
  print(f"🔨 Building {APP_NAME} ({mode}, {win})...")

  result = subprocess.run(cmd)
  if result.returncode != 0:
    print("❌ Build falhou!")
    sys.exit(result.returncode)

  ext = ".exe" if platform.system() == "Windows" else ""
  output = Path("dist") / (APP_NAME if onedir else f"{APP_NAME}{ext}")
  print(f"✅ Pronto! → {output.resolve()}")


def main():
  parser = argparse.ArgumentParser(description="Empacota o Sky Observer.")
  parser.add_argument("--console", action="store_true", help="Console visível (debug)")
  parser.add_argument(
    "--onedir", action="store_true", help="Gera pasta em vez de .exe único"
  )
  args = parser.parse_args()
  build(console=args.console, onedir=args.onedir)


if __name__ == "__main__":
  main()
