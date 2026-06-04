"""Incrementa a versao do projeto no pyproject.toml.

Uso:
  uv run bump patch   # 0.1.0 -> 0.1.1
  uv run bump minor   # 0.1.0 -> 0.2.0
  uv run bump major   # 0.1.0 -> 1.0.0
"""

import re
import sys
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"
VERSION_RE = re.compile(r'^(version\s*=\s*")(\d+\.\d+\.\d+)(")', re.MULTILINE)


def read_version() -> str:
  match = VERSION_RE.search(PYPROJECT.read_text(encoding="utf-8"))
  if not match:
    print("[ERRO] Campo 'version' nao encontrado no pyproject.toml.")
    sys.exit(1)
  return match.group(2)


def bump(part: str) -> str:
  current = read_version()
  major, minor, patch = (int(x) for x in current.split("."))

  if part == "major":
    major += 1
    minor = 0
    patch = 0
  elif part == "minor":
    minor += 1
    patch = 0
  elif part == "patch":
    patch += 1
  else:
    print(f"[ERRO] Parte invalida: '{part}'. Use: major, minor ou patch.")
    sys.exit(1)

  new_version = f"{major}.{minor}.{patch}"
  content = PYPROJECT.read_text(encoding="utf-8")
  content = VERSION_RE.sub(rf"\g<1>{new_version}\g<3>", content)
  PYPROJECT.write_text(content, encoding="utf-8")
  return new_version


def main():
  if len(sys.argv) < 2:
    print(f"Versao atual: {read_version()}")
    print("Uso: uv run bump <major|minor|patch>")
    return

  part = sys.argv[1].lower()
  old = read_version()
  new = bump(part)
  print(f"{old} -> {new}")


if __name__ == "__main__":
  main()
