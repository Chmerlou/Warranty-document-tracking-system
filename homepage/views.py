"""Представления главной страницы и общих ошибок сайта."""

from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from warranties.models import WarrantyDocument


def index(request: HttpRequest) -> HttpResponse:
    """Показать главную страницу со сводкой, рассчитанной через ORM."""
    summary = WarrantyDocument.objects.aggregate(
        document_count=Count("id"),
        active_count=Count(
            "id",
            filter=Q(end_date__gte=timezone.localdate()),
        ),
        client_count=Count("client_id", distinct=True),
    )
    return render(request, "homepage/index.html", summary)


def page_not_found(
    request: HttpRequest,
    exception: Exception,
) -> HttpResponse:
    """Показать оформленную страницу для неизвестного адреса."""
    return render(request, "404.html", status=404)
