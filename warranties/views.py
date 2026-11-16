"""Веб-страницы гарантийных документов."""

from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from storage import load_documents
from warranty_documents import find_warranty_document_by_id

DATA_FILE = Path(settings.BASE_DIR) / "data" / "warranty_documents.json"


def _data_error(request: HttpRequest, error: ValueError) -> HttpResponse:
    """Показать шаблон ошибки загрузки гарантийных документов."""
    return render(
        request,
        "data_error.html",
        {
            "title": "Ошибка данных",
            "heading": "Не удалось загрузить документы",
            "message": str(error),
        },
        status=500,
    )


def warranty_list(request: HttpRequest) -> HttpResponse:
    """Показать список объектов WarrantyDocument из JSON."""
    try:
        documents = load_documents(DATA_FILE)
    except ValueError as error:
        return _data_error(request, error)

    return render(
        request,
        "warranties/warranty_list.html",
        {"documents": documents},
    )


def warranty_detail(
    request: HttpRequest,
    document_id: int,
) -> HttpResponse:
    """Показать объект гарантийного документа по динамическому URL."""
    try:
        documents = load_documents(DATA_FILE)
    except ValueError as error:
        return _data_error(request, error)

    document = find_warranty_document_by_id(documents, document_id)
    return render(
        request,
        "warranties/warranty_detail.html",
        {"document": document},
        status=404 if document is None else 200,
    )
