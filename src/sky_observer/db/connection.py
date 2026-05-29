import sqlite3

# Variável de uso interno que recebe tipo Connection ou None
_conn: sqlite3.Connection | None = None

# Conecta com o db
def get_connection(db_path: str = "app.db") -> sqlite3.Connection:
    global _conn
    if _conn is None:
        # check_same_thread=False segundo o claude é necessário,
        # mas é pra usar threading.Lock se ficar pesado
        _conn = sqlite3.connect(db_path, check_same_thread=False)
        # Retorna o resultado como objeto sqlite3.Row, saindo em forma de dicionário
        _conn.row_factory = sqlite3.Row
    return _conn
