"""Тесты схемы SQLite и переноса данных из JSON."""

import sqlite3
from contextlib import closing

import pytest

from db.database import create_schema, get_connection
from db.import_json import import_json_data


def test_import_creates_tables_and_transfers_all_documents(tmp_path) -> None:
    database_path = tmp_path / "warranty_tracker.sqlite"

    import_json_data(database_path=database_path)

    with closing(get_connection(database_path)) as connection:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        ).fetchall()
        table_names = {row["name"] for row in tables}
        assert table_names == {
            "clients",
            "products",
            "sellers",
            "warranty_documents",
        }
        counts = {
            table: connection.execute(
                f"SELECT COUNT(*) AS count FROM {table}"
            ).fetchone()["count"]
            for table in table_names
        }

    assert counts == {
        "clients": 2,
        "products": 2,
        "sellers": 2,
        "warranty_documents": 2,
    }


def test_connection_enables_foreign_keys_and_named_rows(tmp_path) -> None:
    database_path = tmp_path / "foreign_keys.sqlite"

    with closing(get_connection(database_path)) as connection:
        create_schema(connection)
        foreign_keys = connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]
        row = connection.execute(
            "SELECT 7 AS identifier"
        ).fetchone()

        assert foreign_keys == 1
        assert isinstance(row, sqlite3.Row)
        assert row["identifier"] == 7

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
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
                (1, "INVALID", 99, 99, 99, "2026-01-01", 12, "2027-01-01"),
            )


def test_json_import_can_be_repeated_without_duplicates(tmp_path) -> None:
    database_path = tmp_path / "repeatable.sqlite"

    import_json_data(database_path=database_path)
    import_json_data(database_path=database_path)

    with closing(get_connection(database_path)) as connection:
        count = connection.execute(
            "SELECT COUNT(*) AS count FROM warranty_documents"
        ).fetchone()["count"]

    assert count == 2
