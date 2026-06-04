import os
import sys
import sqlite3

# Variável de uso interno que recebe tipo Connection ou None
_conn: sqlite3.Connection | None = None


def _resolve_db_path(db_name: str) -> str:
    """Resolve o caminho do banco de dados para funcionar tanto em dev quanto empacotado.

    Quando empacotado pelo PyInstaller (--onefile), os arquivos são extraídos para
    um diretório temporário (sys._MEIPASS). Porém, o banco de dados precisa ficar
    persistente ao lado do executável, não no diretório temporário.
    """
    if getattr(sys, "frozen", False):
        # Executável empacotado: o banco fica ao lado do .exe
        base_dir = os.path.dirname(sys.executable)
    else:
        # Desenvolvimento: comportamento padrão (diretório atual)
        base_dir = os.getcwd()
    return os.path.join(base_dir, db_name)


# Conecta com o db
def get_connection(db_path: str = "app.db") -> sqlite3.Connection:
    global _conn
    if _conn is None:
        resolved_path = _resolve_db_path(db_path)
        # usar o threading.Lock se ficar pesado
        _conn = sqlite3.connect(resolved_path, check_same_thread=False)
        # Retorna o resultado como objeto sqlite3.Row, saindo em forma de dicionário
        _conn.row_factory = sqlite3.Row
    return _conn
