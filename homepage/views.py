"""Представления главной страницы и общих ошибок сайта."""

from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from storage import load_documents
from warranty_documents import get_unique_clients

DATA_FILE = Path(settings.BASE_DIR) / "data" / "warranty_documents.json"


def index(request: HttpRequest) -> HttpResponse:
    """Показать главную страницу с показателями реальных данных."""
    try:
        documents = load_documents(DATA_FILE)
    except ValueError as error:
        return render(
            request,
            "data_error.html",
            {
                "title": "Ошибка данных",
                "heading": "Данные временно недоступны",
                "message": str(error),
            },
            status=500,
        )

    active_count = sum(
        document.get_status() != "Гарантия истекла"
        for document in documents
    )
    context = {
        "document_count": len(documents),
        "active_count": active_count,
        "client_count": len(get_unique_clients(documents)),
    }
    return render(request, "homepage/index.html", context)


def page_not_found(
    request: HttpRequest,
    exception: Exception,
) -> HttpResponse:
    """Показать оформленную страницу для неизвестного адреса."""
    return render(request, "404.html", status=404)
