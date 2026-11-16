"""Настроенная административная панель гарантийного реестра."""

from django.contrib import admin, messages
from django.db.models import Count

from .models import Product, Seller, WarrantyDocument


class ProductWarrantyDocumentInline(admin.TabularInline):
    """Документы выбранного товара."""

    model = WarrantyDocument
    fields = ("doc_number", "client", "seller", "end_date", "state")
    extra = 0
    can_delete = False
    show_change_link = True
    autocomplete_fields = ("client", "seller")


class SellerWarrantyDocumentInline(admin.TabularInline):
    """Документы выбранного продавца."""

    model = WarrantyDocument
    fields = ("doc_number", "client", "product", "end_date", "state")
    extra = 0
    can_delete = False
    show_change_link = True
    autocomplete_fields = ("client", "product")


class RelatedDocumentCountAdmin(admin.ModelAdmin):
    """Общие настройки справочников с подсчётом документов."""

    list_display = ("id", "name", "documents_count")
    list_display_links = ("name",)
    search_fields = ("name",)
    ordering = ("name", "id")
    list_per_page = 20
    readonly_fields = ("id",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            related_documents_count=Count("warranty_documents"),
        )

    @admin.display(
        description="Документов",
        ordering="related_documents_count",
    )
    def documents_count(self, obj):
        return obj.related_documents_count


@admin.register(Product)
class ProductAdmin(RelatedDocumentCountAdmin):
    inlines = (ProductWarrantyDocumentInline,)


@admin.register(Seller)
class SellerAdmin(RelatedDocumentCountAdmin):
    inlines = (SellerWarrantyDocumentInline,)


@admin.register(WarrantyDocument)
class WarrantyDocumentAdmin(admin.ModelAdmin):
    """Полная настройка списка и формы гарантийных документов."""

    list_display = (
        "id",
        "doc_number",
        "client",
        "product",
        "seller",
        "end_date",
        "status_label",
        "is_extended_warranty",
        "state",
    )
    list_display_links = ("doc_number",)
    list_editable = ("state",)
    search_fields = (
        "doc_number",
        "client__name",
        "product__name",
        "seller__name",
    )
    list_filter = (
        "state",
        "is_extended_warranty",
        "end_date",
        "client",
        "product",
        "seller",
    )
    ordering = ("end_date", "doc_number")
    list_per_page = 20
    list_select_related = ("client", "product", "seller")
    readonly_fields = ("id", "slug", "is_extended_warranty", "status_label")
    autocomplete_fields = ("client", "product", "seller")
    date_hierarchy = "end_date"
    actions = ("annul_documents", "restore_documents")
    view_on_site = True

    @admin.display(description="Текущий статус", ordering="end_date")
    def status_label(self, obj):
        return obj.status

    @admin.action(description="Аннулировать выбранные документы")
    def annul_documents(self, request, queryset):
        updated = queryset.exclude(
            state=WarrantyDocument.State.ANNULLED
        ).update(state=WarrantyDocument.State.ANNULLED)
        self.message_user(
            request,
            f"Аннулировано документов: {updated}.",
            messages.SUCCESS,
        )

    @admin.action(description="Вернуть выбранные документы в действительные")
    def restore_documents(self, request, queryset):
        updated = queryset.update(state=WarrantyDocument.State.VALID)
        self.message_user(
            request,
            f"Восстановлено документов: {updated}.",
            messages.SUCCESS,
        )
