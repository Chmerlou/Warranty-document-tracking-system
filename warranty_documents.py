"""Функции обработки коллекции объектов гарантийных документов."""

from datetime import date
from typing import Optional

from models import Client, Product, Seller, WarrantyDocument


def calculate_end_date(start_date: date, months: int) -> date:
    """Сохранить интерфейс ПР1 и передать расчет объектной модели."""
    return WarrantyDocument.calculate_end_date(start_date, months)


def get_warranty_status(
    end_date: date,
    today: Optional[date] = None,
) -> str:
    """Сохранить интерфейс ПР1 и передать расчет объектной модели."""
    return WarrantyDocument.status_for_date(end_date, today)


def days_until_expiration(
    end_date: date,
    today: Optional[date] = None,
) -> int:
    """Сохранить интерфейс ПР1 и передать расчет объектной модели."""
    return WarrantyDocument.days_for_date(end_date, today)


def get_expiration_notice(days_left: int, status: str) -> str:
    """Сохранить интерфейс ПР1 и передать формирование уведомления модели."""
    return WarrantyDocument.notice_for(days_left, status)


def _next_document_id(documents: list[WarrantyDocument]) -> int:
    """Определить следующий свободный идентификатор документа."""
    identifiers = [document.id for document in documents]
    return max(identifiers, default=0) + 1


def create_warranty_document(
    documents: list[WarrantyDocument],
    doc_number: str,
    client_name: str,
    product_name: str,
    seller_name: str,
    start_date: date,
    warranty_months: int,
) -> WarrantyDocument:
    """Создать связанные объекты и добавить документ в коллекцию."""
    normalized_number = doc_number.strip()
    if any(
        document.doc_number == normalized_number
        for document in documents
    ):
        raise ValueError("Документ с таким номером уже существует")

    document_id = _next_document_id(documents)
    client = Client(document_id, client_name)
    product = Product(document_id, product_name)
    seller = Seller(document_id, seller_name)
    document = WarrantyDocument(
        document_id,
        normalized_number,
        client,
        product,
        seller,
        start_date,
        warranty_months,
    )
    documents.append(document)
    return document


def find_warranty_documents(
    documents: list[WarrantyDocument],
    query: str,
) -> list[WarrantyDocument]:
    """Найти объекты документов по данным связанных сущностей."""
    return [document for document in documents if document.matches(query)]


def find_warranty_document_by_id(
    documents: list[WarrantyDocument],
    document_id: int,
) -> Optional[WarrantyDocument]:
    """Найти объект гарантийного документа по идентификатору."""
    for document in documents:
        if document.id == document_id:
            return document
    return None


def get_unique_clients(documents: list[WarrantyDocument]) -> list[Client]:
    """Получить уникальных клиентов из коллекции документов."""
    clients_by_id = {}
    for document in documents:
        clients_by_id[document.client.id] = document.client
    return sorted(clients_by_id.values(), key=lambda client: client.name)


def find_client_by_id(
    documents: list[WarrantyDocument],
    client_id: int,
) -> Optional[Client]:
    """Найти клиента по идентификатору среди связанных объектов."""
    for client in get_unique_clients(documents):
        if client.id == client_id:
            return client
    return None


def find_documents_by_client(
    documents: list[WarrantyDocument],
    client_id: int,
) -> list[WarrantyDocument]:
    """Получить все гарантийные документы выбранного клиента."""
    return [
        document
        for document in documents
        if document.client.id == client_id
    ]


def filter_documents_by_status(
    documents: list[WarrantyDocument],
    status: str,
    today: Optional[date] = None,
) -> list[WarrantyDocument]:
    """Отобрать документы с указанным статусом гарантии."""
    return [
        document
        for document in documents
        if document.get_status(today) == status
    ]


def filter_expiring_documents(
    documents: list[WarrantyDocument],
    days: int = 30,
    today: Optional[date] = None,
) -> list[WarrantyDocument]:
    """Отобрать гарантии, истекающие в указанный период."""
    return [
        document
        for document in documents
        if document.expires_within(days, today)
    ]


def sort_warranty_documents(
    documents: list[WarrantyDocument],
    field: str = "end_date",
) -> list[WarrantyDocument]:
    """Вернуть новую коллекцию объектов, отсортированную по полю."""
    field_accessors = {
        "doc_number": lambda document: document.doc_number,
        "client_name": lambda document: document.client.name,
        "product_name": lambda document: document.product.name,
        "seller": lambda document: document.seller.name,
        "start_date": lambda document: document.start_date,
        "end_date": lambda document: document.end_date,
    }
    if field not in field_accessors:
        raise ValueError("Недопустимое поле сортировки")
    return sorted(documents, key=field_accessors[field])


def delete_warranty_document(
    documents: list[WarrantyDocument],
    doc_number: str,
) -> bool:
    """Удалить объект документа по номеру и сообщить результат."""
    for index, document in enumerate(documents):
        if document.doc_number == doc_number.strip():
            del documents[index]
            return True
    return False


def show_warranty_documents(documents: list[WarrantyDocument]) -> None:
    """Вывести коллекцию объектов гарантийных документов."""
    if not documents:
        print("Гарантийные документы не найдены.")
        return

    for document in documents:
        print("-" * 60)
        print(document)
