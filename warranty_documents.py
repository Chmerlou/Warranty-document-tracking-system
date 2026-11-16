"""Функции работы с гарантийными документами."""

import calendar
from datetime import date
from typing import Any, Optional

WarrantyDocument = dict[str, Any]


def calculate_end_date(start_date: date, months: int) -> date:
    """Рассчитать дату окончания гарантии через указанное число месяцев."""
    if months <= 0:
        raise ValueError("Срок гарантии должен быть положительным")

    total_months = start_date.month + months - 1
    year = start_date.year + total_months // 12
    month = total_months % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(start_date.day, last_day)
    return date(year, month, day)


def get_warranty_status(
    end_date: date,
    today: Optional[date] = None,
) -> str:
    """Вернуть статус гарантии относительно указанной или текущей даты."""
    current_date = today or date.today()
    if current_date > end_date:
        return "Гарантия истекла"
    if current_date == end_date:
        return "Последний день гарантии"
    return "Гарантия действует"


def days_until_expiration(
    end_date: date,
    today: Optional[date] = None,
) -> int:
    """Вернуть число дней до окончания гарантии, но не меньше нуля."""
    current_date = today or date.today()
    return max((end_date - current_date).days, 0)


def get_expiration_notice(days_left: int, status: str) -> str:
    """Сформировать уведомление с учетом срока и статуса гарантии."""
    if status == "Гарантия истекла":
        return "Уведомление: гарантия уже истекла"
    if days_left == 0:
        return "Уведомление: сегодня последний день гарантии!"
    if days_left <= 30:
        return "Уведомление: гарантия истекает в течение месяца!"
    return "Гарантия в порядке, уведомлений нет"


def _next_document_id(documents: list[WarrantyDocument]) -> int:
    """Определить следующий свободный числовой идентификатор."""
    identifiers = [
        document.get("id", 0)
        for document in documents
        if isinstance(document.get("id", 0), int)
    ]
    return max(identifiers, default=0) + 1


def _document_end_date(document: WarrantyDocument) -> date:
    """Получить дату окончания из словаря документа."""
    value = document.get("end_date")
    if not isinstance(value, str):
        raise ValueError("В документе отсутствует корректная дата окончания")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        message = "Дата окончания должна иметь формат ГГГГ-ММ-ДД"
        raise ValueError(message) from error


def create_warranty_document(
    documents: list[WarrantyDocument],
    doc_number: str,
    client_name: str,
    product_name: str,
    seller: str,
    start_date: date,
    warranty_months: int,
) -> WarrantyDocument:
    """Создать гарантийный документ и добавить его в коллекцию."""
    normalized_number = doc_number.strip()
    if not normalized_number:
        raise ValueError("Номер документа не может быть пустым")
    if any(
        document.get("doc_number") == normalized_number
        for document in documents
    ):
        raise ValueError("Документ с таким номером уже существует")

    end_date = calculate_end_date(start_date, warranty_months)
    document: WarrantyDocument = {
        "id": _next_document_id(documents),
        "doc_number": normalized_number,
        "client_name": client_name.strip(),
        "product_name": product_name.strip(),
        "seller": seller.strip(),
        "start_date": start_date.isoformat(),
        "warranty_months": warranty_months,
        "end_date": end_date.isoformat(),
    }
    documents.append(document)
    return document


def find_warranty_documents(
    documents: list[WarrantyDocument],
    query: str,
) -> list[WarrantyDocument]:
    """Найти документы по номеру, клиенту, товару или продавцу."""
    normalized_query = query.strip().lower()
    searchable_fields = (
        "doc_number",
        "client_name",
        "product_name",
        "seller",
    )
    return [
        document
        for document in documents
        if any(
            normalized_query in str(document.get(field, "")).lower()
            for field in searchable_fields
        )
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
        if get_warranty_status(_document_end_date(document), today) == status
    ]


def filter_expiring_documents(
    documents: list[WarrantyDocument],
    days: int = 30,
    today: Optional[date] = None,
) -> list[WarrantyDocument]:
    """Отобрать действующие гарантии, истекающие в заданный срок."""
    if days < 0:
        raise ValueError("Период отбора не может быть отрицательным")

    current_date = today or date.today()
    result = []
    for document in documents:
        days_left = (_document_end_date(document) - current_date).days
        if 0 <= days_left <= days:
            result.append(document)
    return result


def sort_warranty_documents(
    documents: list[WarrantyDocument],
    field: str = "end_date",
) -> list[WarrantyDocument]:
    """Вернуть новую коллекцию документов, отсортированную по полю."""
    allowed_fields = {
        "doc_number",
        "client_name",
        "product_name",
        "seller",
        "start_date",
        "end_date",
    }
    if field not in allowed_fields:
        raise ValueError("Недопустимое поле сортировки")
    return sorted(documents, key=lambda document: str(document.get(field, "")))


def delete_warranty_document(
    documents: list[WarrantyDocument],
    doc_number: str,
) -> bool:
    """Удалить документ по номеру и сообщить, был ли он найден."""
    for index, document in enumerate(documents):
        if document.get("doc_number") == doc_number.strip():
            del documents[index]
            return True
    return False


def format_warranty_document(
    document: WarrantyDocument,
    today: Optional[date] = None,
) -> str:
    """Сформировать многострочное представление документа."""
    end_date = _document_end_date(document)
    status = get_warranty_status(end_date, today)
    days_left = days_until_expiration(end_date, today)
    notice = get_expiration_notice(days_left, status)
    return (
        f"№ {document.get('doc_number', '-')} | "
        f"{document.get('product_name', '-')}\n"
        f"Клиент: {document.get('client_name', '-')} | "
        f"Продавец: {document.get('seller', '-')}\n"
        f"Гарантия: {document.get('start_date', '-')} - "
        f"{document.get('end_date', '-')} | {status}\n"
        f"Осталось дней: {days_left}. {notice}"
    )


def show_warranty_documents(documents: list[WarrantyDocument]) -> None:
    """Вывести коллекцию документов в консоль."""
    if not documents:
        print("Гарантийные документы не найдены.")
        return

    for document in documents:
        print("-" * 60)
        print(format_warranty_document(document))
