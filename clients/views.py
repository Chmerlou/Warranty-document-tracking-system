"""Веб-страницы клиентов и связанных гарантий из SQLite."""

import sqlite3
from contextlib import closing

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection
from db.queries import DOCUMENT_FIELDS


def _data_error(
    request: HttpRequest,
    error: sqlite3.Error,
) -> HttpResponse:
    """Показать шаблон ошибки чтения SQLite."""
    return render(
        request,
        "data_error.html",
        {
            "title": "Ошибка базы данных",
            "heading": "Не удалось загрузить клиентов",
            "message": str(error),
        },
        status=500,
    )


def client_list(request: HttpRequest) -> HttpResponse:
    """Показать клиентов и количество их документов из SQLite."""
    try:
        with closing(get_connection()) as connection:
            clients = connection.execute(
                """
                SELECT
                    clients.id,
                    clients.name,
                    COUNT(warranty_documents.id) AS documents_count,
                    MIN(warranty_documents.end_date) AS nearest_end_date
                FROM clients
                LEFT JOIN warranty_documents
                    ON warranty_documents.client_id = clients.id
                GROUP BY clients.id, clients.name
                ORDER BY clients.name
                """
            ).fetchall()
    except sqlite3.Error as error:
        return _data_error(request, error)

    return render(
        request,
        "clients/client_list.html",
        {"clients": clients},
    )


def client_detail(
    request: HttpRequest,
    client_id: int,
) -> HttpResponse:
    """Показать клиента и его документы через связанные запросы."""
    try:
        with closing(get_connection()) as connection:
            client = connection.execute(
                """
                SELECT id, name
                FROM clients
                WHERE id = ?
                """,
                (client_id,),
            ).fetchone()
            documents = []
            if client is not None:
                documents = connection.execute(
                    DOCUMENT_FIELDS
                    + """
                    WHERE warranty_documents.client_id = ?
                    ORDER BY warranty_documents.end_date,
                             warranty_documents.doc_number
                    """,
                    (client_id,),
                ).fetchall()
    except sqlite3.Error as error:
        return _data_error(request, error)

    return render(
        request,
        "clients/client_detail.html",
        {
            "client": client,
            "documents": documents,
        },
        status=404 if client is None else 200,
    )
