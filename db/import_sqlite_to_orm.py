"""Повторяемый перенос данных ПР7 из SQLite в модели Django ORM."""

import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

import django
from django.db import transaction

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DB = BASE_DIR / "data" / "warranty_tracker.sqlite"

sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "warranty_tracker.settings")
django.setup()

from clients.models import Client  # noqa: E402
from warranties.models import Product, Seller, WarrantyDocument  # noqa: E402


def main() -> None:
    """Перенести справочники и документы одной транзакцией."""
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {SOURCE_DB}")

    with sqlite3.connect(SOURCE_DB) as connection:
        connection.row_factory = sqlite3.Row
        clients = connection.execute(
            "SELECT id, name FROM clients ORDER BY id"
        ).fetchall()
        products = connection.execute(
            "SELECT id, name FROM products ORDER BY id"
        ).fetchall()
        sellers = connection.execute(
            "SELECT id, name FROM sellers ORDER BY id"
        ).fetchall()
        documents = connection.execute(
            """
            SELECT id, doc_number, client_id, product_id, seller_id,
                   start_date, warranty_months, end_date
            FROM warranty_documents
            ORDER BY id
            """
        ).fetchall()

    with transaction.atomic():
        for row in clients:
            Client.objects.update_or_create(
                pk=row["id"],
                defaults={"name": row["name"]},
            )
        for row in products:
            Product.objects.update_or_create(
                pk=row["id"],
                defaults={"name": row["name"]},
            )
        for row in sellers:
            Seller.objects.update_or_create(
                pk=row["id"],
                defaults={"name": row["name"]},
            )
        for row in documents:
            WarrantyDocument.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "doc_number": row["doc_number"],
                    "client_id": row["client_id"],
                    "product_id": row["product_id"],
                    "seller_id": row["seller_id"],
                    "start_date": date.fromisoformat(row["start_date"]),
                    "warranty_months": row["warranty_months"],
                    "end_date": date.fromisoformat(row["end_date"]),
                },
            )

    print("Перенос данных завершён.")
    print(f"Клиентов: {Client.objects.count()}")
    print(f"Товаров: {Product.objects.count()}")
    print(f"Продавцов: {Seller.objects.count()}")
    print(f"Документов: {WarrantyDocument.objects.count()}")


if __name__ == "__main__":
    main()
