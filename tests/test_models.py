"""Тесты объектной модели предметной области."""

from datetime import date

import pytest

from models import Client, Party, Product, Seller, WarrantyDocument


def make_document() -> WarrantyDocument:
    """Создать объект документа со связанными сущностями."""
    return WarrantyDocument(
        1,
        "WRT-001",
        Client(1, "Иванов Иван"),
        Product(1, "Ноутбук"),
        Seller(1, "ООО Продавец"),
        date(2026, 1, 31),
        1,
    )


def test_document_contains_related_objects() -> None:
    document = make_document()
    assert isinstance(document.client, Client)
    assert isinstance(document.product, Product)
    assert isinstance(document.seller, Seller)
    assert document.client.name == "Иванов Иван"


def test_inheritance_and_polymorphic_string_representation() -> None:
    parties: list[Party] = [
        Client(1, "Иванов Иван"),
        Seller(2, "ООО Продавец"),
    ]
    assert [str(party) for party in parties] == [
        "Клиент: Иванов Иван",
        "Продавец: ООО Продавец",
    ]


def test_document_methods_calculate_warranty_state() -> None:
    document = make_document()
    assert document.end_date == date(2026, 2, 28)
    assert document.get_status(date(2026, 2, 1)) == "Гарантия действует"
    assert document.days_until_expiration(date(2026, 2, 1)) == 27
    assert document.expires_within(30, date(2026, 2, 1)) is True


def test_string_representation_contains_related_names() -> None:
    result = str(make_document())
    assert "WRT-001" in result
    assert "Иванов Иван" in result
    assert "Ноутбук" in result
    assert "ООО Продавец" in result


def test_encapsulated_values_are_available_through_properties() -> None:
    document = make_document()
    assert document.id == 1
    assert document.doc_number == "WRT-001"
    assert document.warranty_months == 1


def test_invalid_warranty_period_is_rejected() -> None:
    with pytest.raises(ValueError, match="положительным"):
        WarrantyDocument(
            1,
            "WRT-001",
            Client(1, "Иванов Иван"),
            Product(1, "Ноутбук"),
            Seller(1, "ООО Продавец"),
            date(2026, 1, 1),
            0,
        )


def test_object_json_conversion_round_trip() -> None:
    original = make_document()
    restored = WarrantyDocument.from_dict(original.to_dict())
    assert restored.doc_number == original.doc_number
    assert restored.client.name == original.client.name
    assert restored.product.name == original.product.name
    assert restored.end_date == original.end_date
