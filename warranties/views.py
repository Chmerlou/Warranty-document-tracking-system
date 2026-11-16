"""Веб-страницы гарантийных документов из SQLite."""

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
            "heading": "Не удалось загрузить документы",
            "message": str(error),
        },
        status=500,
    )


def warranty_list(request: HttpRequest) -> HttpResponse:
    """Показать связанные данные документов из SQLite."""
    try:
        with closing(get_connection()) as connection:
            documents = connection.execute(
                DOCUMENT_FIELDS
                + """
                ORDER BY warranty_documents.end_date,
                         warranty_documents.doc_number
                """
            ).fetchall()
    except sqlite3.Error as error:
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
    """Показать документ по параметризованному SQL-запросу."""
    try:
        with closing(get_connection()) as connection:
            document = connection.execute(
                DOCUMENT_FIELDS + " WHERE warranty_documents.id = ?",
                (document_id,),
            ).fetchone()
    except sqlite3.Error as error:
        return _data_error(request, error)

    return render(
        request,
        "warranties/warranty_detail.html",
        {"document": document},
        status=404 if document is None else 200,
    )


def warranty_search(request: HttpRequest) -> HttpResponse:
    """Найти документы по номеру или связанным названиям."""
    query = request.GET.get("q", "").strip()
    documents = []
    if query:
        pattern = f"%{query}%"
        try:
            with closing(get_connection()) as connection:
                documents = connection.execute(
                    DOCUMENT_FIELDS
                    + """
                    WHERE lower(warranty_documents.doc_number) LIKE lower(?)
                       OR lower(clients.name) LIKE lower(?)
                       OR lower(products.name) LIKE lower(?)
                       OR lower(sellers.name) LIKE lower(?)
                    ORDER BY warranty_documents.end_date,
                             warranty_documents.doc_number
                    """,
                    (pattern, pattern, pattern, pattern),
                ).fetchall()
        except sqlite3.Error as error:
            return _data_error(request, error)

    return render(
        request,
        "warranties/warranty_search.html",
        {
            "documents": documents,
            "query": query,
            "searched": bool(query),
        },
    )


def warranty_statistics(request: HttpRequest) -> HttpResponse:
    """Показать агрегаты и группировки по гарантийному реестру."""
    try:
        with closing(get_connection()) as connection:
            status_statistics = connection.execute(
                """
                SELECT
                    CASE
                        WHEN date(end_date) < date('now', 'localtime')
                            THEN 'Гарантия истекла'
                        WHEN date(end_date) = date('now', 'localtime')
                            THEN 'Последний день гарантии'
                        ELSE 'Гарантия действует'
                    END AS status,
                    COUNT(*) AS documents_count
                FROM warranty_documents
                GROUP BY status
                ORDER BY documents_count DESC, status
                """
            ).fetchall()
            client_statistics = connection.execute(
                """
                SELECT
                    clients.id,
                    clients.name AS client_name,
                    COUNT(warranty_documents.id) AS documents_count,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN date(warranty_documents.end_date)
                                    >= date('now', 'localtime')
                                THEN 1
                                ELSE 0
                            END
                        ),
                        0
                    ) AS active_count
                FROM clients
                LEFT JOIN warranty_documents
                    ON warranty_documents.client_id = clients.id
                GROUP BY clients.id, clients.name
                ORDER BY documents_count DESC, clients.name
                """
            ).fetchall()
            repeat_clients = connection.execute(
                """
                SELECT
                    clients.name AS client_name,
                    COUNT(warranty_documents.id) AS documents_count
                FROM clients
                JOIN warranty_documents
                    ON warranty_documents.client_id = clients.id
                GROUP BY clients.id, clients.name
                HAVING COUNT(warranty_documents.id) > 1
                ORDER BY documents_count DESC, clients.name
                """
            ).fetchall()
    except sqlite3.Error as error:
        return _data_error(request, error)

    return render(
        request,
        "warranties/statistics.html",
        {
            "status_statistics": status_statistics,
            "client_statistics": client_statistics,
            "repeat_clients": repeat_clients,
        },
    )
