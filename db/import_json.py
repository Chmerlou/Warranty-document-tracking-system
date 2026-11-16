"""Однократный перенос существующих JSON-данных в SQLite."""

import sqlite3
from pathlib import Path
from typing import Iterable

from models import WarrantyDocument
from storage import load_documents

from db.database import DB_PATH, PROJECT_ROOT, create_schema, get_connection

JSON_PATH = PROJECT_ROOT / "data" / "warranty_documents.json"


def _unique_rows(
    rows: Iterable[tuple[int, str]],
    entity_name: str,
) -> list[tuple[int, str]]:
    """Проверить уникальность идентификаторов связанных сущностей."""
    names_by_id: dict[int, str] = {}
    for identifier, name in rows:
        existing_name = names_by_id.get(identifier)
        if existing_name is not None and existing_name != name:
            message = (
                f"{entity_name} с ID {identifier} имеет разные названия"
            )
            raise ValueError(message)
        names_by_id[identifier] = name
    return sorted(names_by_id.items())


def import_documents(
    connection: sqlite3.Connection,
    documents: list[WarrantyDocument],
) -> None:
    """Заменить содержимое таблиц данными предметных объектов."""
    clients = _unique_rows(
        ((item.client.id, item.client.name) for item in documents),
        "Клиент",
    )
    products = _unique_rows(
        ((item.product.id, item.product.name) for item in documents),
        "Товар",
    )
    sellers = _unique_rows(
        ((item.seller.id, item.seller.name) for item in documents),
        "Продавец",
    )

    connection.execute("DELETE FROM warranty_documents")
    connection.execute("DELETE FROM clients")
    connection.execute("DELETE FROM products")
    connection.execute("DELETE FROM sellers")

    connection.executemany(
        "INSERT INTO clients (id, name) VALUES (?, ?)",
        clients,
    )
    connection.executemany(
        "INSERT INTO products (id, name) VALUES (?, ?)",
        products,
    )
    connection.executemany(
        "INSERT INTO sellers (id, name) VALUES (?, ?)",
        sellers,
    )
    connection.executemany(
        """
        INSERT INTO warranty_documents (
            id,
            doc_number,
            client_id,
            product_id,
            seller_id,
            start_date,
            warranty_months,
            end_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                item.id,
                item.doc_number,
                item.client.id,
                item.product.id,
                item.seller.id,
                item.start_date.isoformat(),
                item.warranty_months,
                item.end_date.isoformat(),
            )
            for item in documents
        ],
    )


def import_json_data(
    json_path: Path = JSON_PATH,
    database_path: Path = DB_PATH,
) -> None:
    """Создать схему и транзакционно импортировать JSON в SQLite."""
    documents = load_documents(json_path)
    connection = get_connection(database_path)
    try:
        create_schema(connection)
        import_documents(connection, documents)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def main() -> None:
    """Запустить импорт стандартных файлов проекта."""
    import_json_data()


if __name__ == "__main__":
    main()
