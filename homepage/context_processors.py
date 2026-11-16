"""Общие данные, доступные во всех шаблонах проекта."""

from warranties.models import WarrantyDocument


def registry_context(request) -> dict[str, int | str]:
    """Передать название сайта и актуальное число документов."""
    return {
        "site_name": "Гарантийный реестр",
        "registry_documents_count": WarrantyDocument.objects.count(),
    }
