"""Тесты преобразования между JSON и объектной моделью."""

from datetime import date
from pathlib import Path

import pytest

from models import Client, Product, Seller, WarrantyDocument
from storage import load_documents, save_documents


def make_document() -> WarrantyDocument:
    """Создать объект документа для проверки хранилища."""
    return WarrantyDocument(
        1,
        "WRT-001",
        Client(1, "Иванов Иван"),
        Product(1, "Ноутбук"),
        Seller(1, "ООО Продавец"),
        date(2026, 1, 10),
        12,
    )


def test_save_and_load_document_objects(tmp_path: Path) -> None:
    file_path = tmp_path / "documents.json"
    save_documents(file_path, [make_document()])
    documents = load_documents(file_path)
    assert len(documents) == 1
    assert isinstance(documents[0], WarrantyDocument)
    assert isinstance(documents[0].client, Client)
    assert documents[0].doc_number == "WRT-001"


def test_load_old_pr2_format_creates_objects(tmp_path: Path) -> None:
    file_path = tmp_path / "documents.json"
    file_path.write_text(
        """[
          {
            "id": 1,
            "doc_number": "WRT-OLD",
            "client_name": "Иванов Иван",
            "product_name": "Ноутбук",
            "seller": "ООО Продавец",
            "start_date": "2026-01-01",
            "warranty_months": 12,
            "end_date": "2027-01-01"
          }
        ]""",
        encoding="utf-8",
    )
    document = load_documents(file_path)[0]
    assert isinstance(document, WarrantyDocument)
    assert document.client.name == "Иванов Иван"


def test_load_missing_file_returns_empty_list(tmp_path: Path) -> None:
    assert load_documents(tmp_path / "missing.json") == []


def test_load_invalid_json_raises_clear_error(tmp_path: Path) -> None:
    file_path = tmp_path / "broken.json"
    file_path.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError, match="Не удалось прочитать"):
        load_documents(file_path)
