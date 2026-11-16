"""Веб-страницы клиентов и связанных гарантий."""

from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from storage import load_documents
from warranty_documents import (
    find_client_by_id,
    find_documents_by_client,
    get_unique_clients,
)

DATA_FILE = Path(settings.BASE_DIR) / "data" / "warranty_documents.json"


def _data_error(request: HttpRequest, error: ValueError) -> HttpResponse:
    """Показать шаблон ошибки загрузки клиентов."""
    return render(
        request,
        "data_error.html",
        {
            "title": "Ошибка данных",
            "heading": "Не удалось загрузить клиентов",
            "message": str(error),
        },
        status=500,
    )


def client_list(request: HttpRequest) -> HttpResponse:
    """Показать уникальных клиентов из объектов документов."""
    try:
        documents = load_documents(DATA_FILE)
    except ValueError as error:
        return _data_error(request, error)

    return render(
        request,
        "clients/client_list.html",
        {"clients": get_unique_clients(documents)},
    )


def client_detail(
    request: HttpRequest,
    client_id: int,
) -> HttpResponse:
    """Показать клиента и список его гарантий по динамическому URL."""
    try:
        documents = load_documents(DATA_FILE)
    except ValueError as error:
        return _data_error(request, error)

    client = find_client_by_id(documents, client_id)
    client_documents = (
        find_documents_by_client(documents, client_id)
        if client is not None
        else []
    )
    return render(
        request,
        "clients/client_detail.html",
        {
            "client": client,
            "documents": client_documents,
        },
        status=404 if client is None else 200,
    )
