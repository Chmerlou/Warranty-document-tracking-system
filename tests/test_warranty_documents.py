"""Тесты функций обработки коллекции объектов документов."""

from datetime import date

import pytest

from models import WarrantyDocument
from warranty_documents import (
    calculate_end_date,
    create_warranty_document,
    delete_warranty_document,
    filter_documents_by_status,
    filter_expiring_documents,
    find_client_by_id,
    find_documents_by_client,
    find_warranty_document_by_id,
    find_warranty_documents,
    get_unique_clients,
    get_expiration_notice,
    sort_warranty_documents,
)


def make_document(
    documents: list[WarrantyDocument],
    number: str,
    product: str,
    start: date,
    months: int,
) -> WarrantyDocument:
    """Создать тестовый объект документа."""
    return create_warranty_document(
        documents,
        number,
        "Иванов Иван",
        product,
        "Тестовый продавец",
        start,
        months,
    )


def test_calculate_end_date_interface_from_pr1_is_preserved() -> None:
    assert calculate_end_date(date(2024, 1, 31), 1) == date(2024, 2, 29)


def test_create_document_adds_object_to_collection() -> None:
    documents = []
    document = make_document(
        documents,
        "WRT-001",
        "Ноутбук",
        date(2026, 1, 10),
        12,
    )
    assert isinstance(document, WarrantyDocument)
    assert document.end_date == date(2027, 1, 10)
    assert documents == [document]


def test_duplicate_document_number_is_forbidden() -> None:
    documents = []
    make_document(documents, "WRT-001", "Ноутбук", date(2026, 1, 10), 12)
    with pytest.raises(ValueError, match="уже существует"):
        make_document(
            documents,
            "WRT-001",
            "Телефон",
            date(2026, 2, 10),
            12,
        )


def test_find_documents_uses_related_objects() -> None:
    documents = []
    make_document(documents, "WRT-001", "Ноутбук Lenovo", date(2026, 1, 1), 12)
    make_document(documents, "WRT-002", "Телефон", date(2026, 1, 1), 12)
    result = find_warranty_documents(documents, "lenovo")
    assert [document.doc_number for document in result] == ["WRT-001"]


def test_find_objects_for_dynamic_web_pages() -> None:
    documents = []
    make_document(documents, "WRT-001", "Ноутбук", date(2026, 1, 1), 12)
    make_document(documents, "WRT-002", "Телефон", date(2026, 1, 1), 12)
    assert find_warranty_document_by_id(documents, 2) is documents[1]
    assert find_warranty_document_by_id(documents, 404) is None
    assert find_client_by_id(documents, 1) is documents[0].client
    assert [client.id for client in get_unique_clients(documents)] == [1, 2]
    assert find_documents_by_client(documents, 2) == [documents[1]]


def test_filter_documents_by_status_uses_object_method() -> None:
    documents = []
    make_document(documents, "OLD", "Ноутбук", date(2024, 1, 1), 12)
    make_document(documents, "NEW", "Телефон", date(2026, 1, 1), 12)
    result = filter_documents_by_status(
        documents,
        "Гарантия истекла",
        date(2025, 6, 1),
    )
    assert [document.doc_number for document in result] == ["OLD"]


def test_filter_expiring_documents_uses_object_method() -> None:
    documents = []
    make_document(documents, "SOON", "Ноутбук", date(2025, 1, 20), 12)
    make_document(documents, "LATER", "Телефон", date(2025, 3, 1), 12)
    result = filter_expiring_documents(documents, 30, date(2026, 1, 1))
    assert [document.doc_number for document in result] == ["SOON"]


def test_sort_documents_does_not_change_original_order() -> None:
    documents = []
    make_document(documents, "B", "Ноутбук", date(2026, 2, 1), 12)
    make_document(documents, "A", "Телефон", date(2026, 1, 1), 12)
    result = sort_warranty_documents(documents, "doc_number")
    assert [document.doc_number for document in result] == ["A", "B"]
    assert [document.doc_number for document in documents] == ["B", "A"]


def test_delete_document_reports_result() -> None:
    documents = []
    make_document(documents, "WRT-001", "Ноутбук", date(2026, 1, 1), 12)
    assert delete_warranty_document(documents, "WRT-001") is True
    assert delete_warranty_document(documents, "WRT-404") is False
    assert documents == []


def test_notice_distinguishes_last_day_from_expired() -> None:
    assert get_expiration_notice(0, "Последний день гарантии") == (
        "Уведомление: сегодня последний день гарантии!"
    )
    assert get_expiration_notice(0, "Гарантия истекла") == (
        "Уведомление: гарантия уже истекла"
    )
