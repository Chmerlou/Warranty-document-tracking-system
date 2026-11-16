"""Тесты ORM-моделей, маршрутов и представлений Django."""

from datetime import date, timedelta

from django.db.models.deletion import ProtectedError
from django.test import TestCase, override_settings
from django.urls import reverse

from clients.models import Client
from warranties.models import Product, Seller, WarrantyDocument


class WebPageTests(TestCase):
    """Проверить страницы, связи и основные ORM-сценарии проекта."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.client_one = Client.objects.create(name="Иванов Иван Иванович")
        cls.client_two = Client.objects.create(name="Петрова Анна Сергеевна")
        cls.product_one = Product.objects.create(
            name="Ноутбук Lenovo IdeaPad 3"
        )
        cls.product_two = Product.objects.create(
            name="Смартфон Samsung Galaxy A55"
        )
        cls.seller_one = Seller.objects.create(name="ООО «ТехноМир»")
        cls.seller_two = Seller.objects.create(name="ООО «Мобильный мир»")
        today = date.today()
        cls.document_one = WarrantyDocument.objects.create(
            doc_number="WRT-2026-001",
            client=cls.client_one,
            product=cls.product_one,
            seller=cls.seller_one,
            start_date=today - timedelta(days=30),
            warranty_months=24,
            end_date=today + timedelta(days=700),
        )
        cls.document_two = WarrantyDocument.objects.create(
            doc_number="WRT-2026-002",
            client=cls.client_two,
            product=cls.product_two,
            seller=cls.seller_two,
            start_date=today - timedelta(days=700),
            warranty_months=12,
            end_date=today - timedelta(days=1),
        )

    def test_homepage_uses_orm_summary(self) -> None:
        response = self.client.get(reverse("homepage:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "homepage/index.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "Гарантийные документы под контролем")
        self.assertEqual(response.context["document_count"], 2)
        self.assertEqual(response.context["active_count"], 1)

    def test_warranty_list_displays_orm_records(self) -> None:
        response = self.client.get(reverse("warranties:list"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["documents"][0], dict)
        self.assertContains(response, "Ноутбук Lenovo IdeaPad 3")
        self.assertContains(response, "WRT-2026-001")
        self.assertContains(response, "Найдено документов: 2")

    def test_warranty_detail_uses_select_related(self) -> None:
        response = self.client.get(
            reverse("warranties:detail", args=[self.document_one.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Иванов Иван Иванович")
        self.assertContains(response, "ООО «ТехноМир»")

    def test_unknown_warranty_returns_404(self) -> None:
        response = self.client.get(reverse("warranties:detail", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_client_list_and_reverse_relation(self) -> None:
        response = self.client.get(reverse("clients:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Петрова Анна Сергеевна")
        self.assertEqual(self.client_one.warranty_documents.count(), 1)

    def test_client_detail_displays_related_warranty(self) -> None:
        response = self.client.get(
            reverse("clients:detail", args=[self.client_one.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "WRT-2026-001")

    def test_warranty_list_handles_empty_queryset(self) -> None:
        WarrantyDocument.objects.all().delete()
        response = self.client.get(reverse("warranties:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Документы не найдены")

    def test_multi_field_search(self) -> None:
        response = self.client.get(
            reverse("warranties:search"), {"q": "Lenovo"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "WRT-2026-001")
        self.assertContains(response, "Найдено: 1")

    def test_search_does_not_interpret_query_as_sql(self) -> None:
        response = self.client.get(
            reverse("warranties:search"),
            {"q": "' OR 1=1 --"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Совпадений нет")
        self.assertNotContains(response, "Ноутбук Lenovo IdeaPad 3")

    def test_filter_by_status_and_related_client(self) -> None:
        response = self.client.get(
            reverse("warranties:list"),
            {"status": "active", "client": str(self.client_one.pk)},
        )
        self.assertContains(response, "WRT-2026-001")
        self.assertNotContains(response, "WRT-2026-002")

    def test_invalid_filter_and_sort_values_are_safe(self) -> None:
        response = self.client.get(
            reverse("warranties:list"),
            {"client": "invalid", "sort": "__unsafe"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["sort"], "expiry")
        self.assertEqual(response.context["selected_client"], "")

    def test_pagination_preserves_filter_parameters(self) -> None:
        for number in range(3, 9):
            WarrantyDocument.objects.create(
                doc_number=f"WRT-2026-{number:03d}",
                client=self.client_one,
                product=self.product_one,
                seller=self.seller_one,
                start_date=date.today(),
                warranty_months=12,
                end_date=date.today() + timedelta(days=number),
            )
        response = self.client.get(
            reverse("warranties:list"),
            {"status": "active", "sort": "product"},
        )
        self.assertEqual(response.context["page_obj"].paginator.num_pages, 2)
        self.assertContains(response, "status=active")
        self.assertContains(response, "sort=product")

    def test_statistics_use_annotations_and_aggregates(self) -> None:
        response = self.client.get(reverse("warranties:statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Документы по статусам")
        self.assertContains(response, "Гарантия действует")
        self.assertContains(response, "Средний срок, мес.")

    def test_crud_and_protected_relationship(self) -> None:
        document = WarrantyDocument.objects.get(pk=self.document_one.pk)
        document.warranty_months = 36
        document.save(update_fields=["warranty_months"])
        self.assertEqual(
            WarrantyDocument.objects.get(pk=document.pk).warranty_months,
            36,
        )
        with self.assertRaises(ProtectedError):
            self.client_one.delete()
        document.delete()
        self.assertFalse(
            WarrantyDocument.objects.filter(pk=document.pk).exists()
        )

    def test_unknown_client_returns_404(self) -> None:
        response = self.client.get(reverse("clients:detail", args=[999]))
        self.assertEqual(response.status_code, 404)

    @override_settings(DEBUG=False)
    def test_custom_404_page(self) -> None:
        response = self.client.get("/unknown-address/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Страница не найдена", status_code=404)

    def test_pages_include_accessible_navigation(self) -> None:
        response = self.client.get(reverse("homepage:index"))
        self.assertContains(response, "bootstrap@5.3.3")
        self.assertContains(response, 'href="#main-content"')
        self.assertContains(response, 'aria-label="Основная навигация"')
