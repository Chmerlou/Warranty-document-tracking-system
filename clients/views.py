"""Веб-страницы клиентов и связанных гарантий через Django ORM."""

from django.db.models import Count, Min
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Client


def client_list(request: HttpRequest) -> HttpResponse:
    """Показать клиентов с количеством документов и ближайшей датой."""
    clients = Client.objects.annotate(
        documents_count=Count("warranty_documents"),
        nearest_end_date=Min("warranty_documents__end_date"),
    ).order_by("name", "pk")

    return render(
        request,
        "clients/client_list.html",
        {"clients": clients},
    )


def client_detail(
    request: HttpRequest,
    client_id: int,
) -> HttpResponse:
    """Показать клиента и документы через обратную связь модели."""
    client = get_object_or_404(Client, pk=client_id)
    documents = client.warranty_documents.select_related(
        "client",
        "product",
        "seller",
    ).order_by("end_date", "doc_number")

    return render(
        request,
        "clients/client_detail.html",
        {
            "client": client,
            "documents": documents,
        },
    )
