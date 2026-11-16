"""Представления главной страницы и общих ошибок сайта."""

import sqlite3
from contextlib import closing

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection


def index(request: HttpRequest) -> HttpResponse:
    """Показать главную страницу со сводкой из SQLite."""
    try:
        with closing(get_connection()) as connection:
            summary = connection.execute(
                """
                SELECT
                    COUNT(*) AS document_count,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN date(end_date) >= date(
                                    'now', 'localtime'
                                ) THEN 1
                                ELSE 0
                            END
                        ),
                        0
                    ) AS active_count,
                    COUNT(DISTINCT client_id) AS client_count
                FROM warranty_documents
                """
            ).fetchone()
    except sqlite3.Error as error:
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

    return render(request, "homepage/index.html", dict(summary))


def page_not_found(
    request: HttpRequest,
    exception: Exception,
) -> HttpResponse:
    """Показать оформленную страницу для неизвестного адреса."""
    return render(request, "404.html", status=404)
