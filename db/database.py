"""Подключение к SQLite и применение схемы базы данных."""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "warranty_tracker.sqlite"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"


def get_connection(
    database_path: Path | str = DB_PATH,
) -> sqlite3.Connection:
    """Открыть соединение с именованными строками и внешними ключами."""
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_schema(connection: sqlite3.Connection) -> None:
    """Создать таблицы и индексы из файла SQL-схемы."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    connection.executescript(schema)
