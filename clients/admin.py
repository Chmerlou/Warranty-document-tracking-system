"""Административный интерфейс клиентов."""

from django.contrib import admin
from django.db.models import Count, Q
from django.utils import timezone

from warranties.models import WarrantyDocument

from .models import Client


class ClientWarrantyDocumentInline(admin.TabularInline):
    """Связанные документы в карточке клиента."""

    model = WarrantyDocument
    fields = (
        "doc_number",
        "product",
        "seller",
        "end_date",
        "state",
    )
    extra = 0
    can_delete = False
    show_change_link = True
    autocomplete_fields = ("product", "seller")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Поиск клиентов и просмотр их документов без N+1-запросов."""

    list_display = ("id", "name", "active_documents_count")
    list_display_links = ("name",)
    search_fields = ("name",)
    ordering = ("name", "id")
    list_per_page = 20
    readonly_fields = ("id",)
    inlines = (ClientWarrantyDocumentInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            active_documents=Count(
                "warranty_documents",
                filter=Q(
                    warranty_documents__state=(
                        WarrantyDocument.State.VALID
                    ),
                    warranty_documents__end_date__gte=timezone.localdate(),
                ),
            )
        )

    @admin.display(
        description="Действующих гарантий",
        ordering="active_documents",
    )
    def active_documents_count(self, obj):
        return obj.active_documents
