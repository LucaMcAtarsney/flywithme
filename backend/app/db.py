import sqlite3
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
#DB_PATH = "backend/app/flywithme.db" 
DB_PATH = BACKEND_DIR / "flywithme.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # allows us to access columns by name not index
    conn.execute("PRAGMA foreign_keys = ON")
    return conn