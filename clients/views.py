"""Веб-страницы клиентов и связанных гарантий."""

from pathlib import Path
from typing import Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.html import escape

from homepage.views import page
from models import WarrantyDocument
from storage import load_documents
from warranty_documents import (
    find_client_by_id,
    find_documents_by_client,
    get_unique_clients,
)

DATA_FILE = Path(settings.BASE_DIR) / "data" / "warranty_documents.json"


def _load_or_error(
) -> tuple[list[WarrantyDocument], Optional[HttpResponse]]:
    """Загрузить документы или подготовить HTTP-ответ с ошибкой."""
    try:
        return load_documents(DATA_FILE), None
    except ValueError as error:
        content = f"""
        <section class="error-state" role="alert">
            <h1>Не удалось загрузить клиентов</h1>
            <p>{escape(error)}</p>
            <a class="button-link" href="/">Вернуться на главную</a>
        </section>
        """
        response = HttpResponse(
            page("Ошибка данных", content, "/clients/"),
            status=500,
        )
        return [], response


def client_list(request: HttpRequest) -> HttpResponse:
    """Показать уникальных клиентов из объектов документов."""
    documents, error_response = _load_or_error()
    if error_response is not None:
        return error_response

    clients = get_unique_clients(documents)
    if clients:
        items = "".join(
            f"""
            <li>
                <a class="record-list__link" href="/clients/{client.id}/">
                    <span>
                        <span class="record-list__title">
                            {escape(client.name)}
                        </span>
                        <span class="record-list__meta">
                            Клиент №{client.id}
                        </span>
                    </span>
                    <span class="record-list__meta">Открыть профиль</span>
                </a>
            </li>
            """
            for client in clients
        )
        body = f'<ul class="record-list">{items}</ul>'
    else:
        body = """
        <section class="empty-state">
            <h2>Клиентов пока нет</h2>
            <p>Клиенты появятся вместе с гарантийными документами.</p>
        </section>
        """

    content = f"""
    <section class="page-heading">
        <h1>Клиенты</h1>
        <p class="lead-copy">
            Владельцы товаров и связанные с ними гарантии.
        </p>
    </section>
    {body}
    """
    return HttpResponse(page("Клиенты", content, "/clients/"))


def client_detail(
    request: HttpRequest,
    client_id: int,
) -> HttpResponse:
    """Показать клиента и список его гарантий по динамическому URL."""
    documents, error_response = _load_or_error()
    if error_response is not None:
        return error_response

    client = find_client_by_id(documents, client_id)
    if client is None:
        content = """
        <section class="error-state">
            <h1>Клиент не найден</h1>
            <p>В реестре нет клиента с таким ID.</p>
            <a class="button-link" href="/clients/">
                Вернуться к клиентам
            </a>
        </section>
        """
        return HttpResponse(
            page("Клиент не найден", content, "/clients/"),
            status=404,
        )

    client_documents = find_documents_by_client(documents, client_id)
    items = "".join(
        f"""
        <li>
            <a class="record-list__link"
               href="/warranties/{document.id}/">
                <span>
                    <span class="record-list__title">
                        {escape(document.product.name)}
                    </span>
                    <span class="record-list__meta">
                        {escape(document.doc_number)}
                    </span>
                </span>
                <span class="record-list__meta">
                    до {document.end_date:%d.%m.%Y}
                </span>
            </a>
        </li>
        """
        for document in client_documents
    )
    content = f"""
    <section class="page-heading">
        <h1>{escape(client.name)}</h1>
        <p class="lead-copy">
            Гарантийных документов: {len(client_documents)}
        </p>
    </section>
    <section class="detail-panel">
        <h2>Гарантии клиента</h2>
        <ul class="record-list">{items}</ul>
        <div class="action-row mt-4">
            <a class="button-link button-link--secondary" href="/clients/">
                Вернуться к клиентам
            </a>
        </div>
    </section>
    """
    return HttpResponse(page(client.name, content, "/clients/"))
