"""Страницы гарантийных документов на основе Django ORM."""

from django.core.paginator import Paginator
from django.db.models import (
    Avg,
    Case,
    CharField,
    Count,
    F,
    Max,
    Min,
    Q,
    Value,
    When,
)
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from clients.models import Client

from .models import WarrantyDocument


def _status_expression(today):
    """Вернуть вычисляемый ORM-статус гарантии для списка и статистики."""
    return Case(
        When(end_date__lt=today, then=Value("Гарантия истекла")),
        When(end_date=today, then=Value("Последний день гарантии")),
        default=Value("Гарантия действует"),
        output_field=CharField(),
    )


def warranty_list(request: HttpRequest) -> HttpResponse:
    """Показать документы с поиском, фильтрами, сортировкой и страницами."""
    today = timezone.localdate()
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    client_id = request.GET.get("client", "").strip()
    sort = request.GET.get("sort", "expiry").strip()

    documents = WarrantyDocument.objects.all()
    if query:
        documents = documents.filter(
            Q(doc_number__icontains=query)
            | Q(client__name__icontains=query)
            | Q(product__name__icontains=query)
            | Q(seller__name__icontains=query)
        )
    if status == "active":
        documents = documents.exclude(end_date__lt=today)
    elif status == "expired":
        documents = documents.filter(end_date__lt=today)
    elif status == "today":
        documents = documents.filter(end_date=today)
    else:
        status = ""
    if client_id.isdigit():
        documents = documents.filter(client_id=int(client_id))
    elif client_id:
        client_id = ""

    sort_fields = {
        "expiry": ("end_date", "doc_number"),
        "expiry_desc": ("-end_date", "doc_number"),
        "product": ("product__name", "doc_number"),
        "client": ("client__name", "doc_number"),
    }
    if sort not in sort_fields:
        sort = "expiry"

    documents = (
        documents.annotate(
            product_name=F("product__name"),
            client_name=F("client__name"),
            seller_name=F("seller__name"),
            status=_status_expression(today),
        )
        .values(
            "id",
            "doc_number",
            "client_id",
            "product_name",
            "client_name",
            "seller_name",
            "start_date",
            "warranty_months",
            "end_date",
            "status",
        )
        .order_by(*sort_fields[sort])
    )
    paginator = Paginator(documents, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "warranties/warranty_list.html",
        {
            "documents": page_obj,
            "page_obj": page_obj,
            "document_count": paginator.count,
            "query": query,
            "selected_status": status,
            "selected_client": client_id,
            "sort": sort,
            "clients": Client.objects.order_by("name", "pk"),
        },
    )


def warranty_detail(
    request: HttpRequest,
    document_id: int,
) -> HttpResponse:
    """Показать документ и связанные объекты либо вернуть 404."""
    document = get_object_or_404(
        WarrantyDocument.objects.select_related(
            "client",
            "product",
            "seller",
        ),
        pk=document_id,
    )

    return render(
        request,
        "warranties/warranty_detail.html",
        {"document": document},
    )


def warranty_search(request: HttpRequest) -> HttpResponse:
    """Найти документы по номеру и нескольким связанным полям."""
    query = request.GET.get("q", "").strip()
    documents = WarrantyDocument.objects.none()
    if query:
        documents = (
            WarrantyDocument.objects.select_related(
                "client",
                "product",
                "seller",
            )
            .filter(
                Q(doc_number__icontains=query)
                | Q(client__name__icontains=query)
                | Q(product__name__icontains=query)
                | Q(seller__name__icontains=query)
            )
            .order_by("end_date", "doc_number")
        )

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
    """Показать группировки и агрегаты, рассчитанные через ORM."""
    today = timezone.localdate()
    status_statistics = (
        WarrantyDocument.objects.annotate(status=_status_expression(today))
        .values("status")
        .annotate(documents_count=Count("id"))
        .order_by("-documents_count", "status")
    )
    client_statistics = (
        Client.objects.annotate(
            documents_count=Count("warranty_documents"),
            active_count=Count(
                "warranty_documents",
                filter=Q(warranty_documents__end_date__gte=today),
            ),
            client_name=F("name"),
        )
        .values("id", "client_name", "documents_count", "active_count")
        .order_by("-documents_count", "client_name")
    )
    repeat_clients = (
        Client.objects.annotate(
            documents_count=Count("warranty_documents"),
            client_name=F("name"),
        )
        .filter(documents_count__gt=1)
        .values("client_name", "documents_count")
        .order_by("-documents_count", "client_name")
    )
    warranty_summary = WarrantyDocument.objects.aggregate(
        average_months=Avg("warranty_months"),
        earliest_end_date=Min("end_date"),
        latest_end_date=Max("end_date"),
    )

    return render(
        request,
        "warranties/statistics.html",
        {
            "status_statistics": status_statistics,
            "client_statistics": client_statistics,
            "repeat_clients": repeat_clients,
            "warranty_summary": warranty_summary,
        },
    )
