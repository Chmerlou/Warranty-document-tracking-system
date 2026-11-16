"""Тесты маршрутов и view-функций Django-приложения."""

import sqlite3
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings
from django.urls import reverse


class WebPageTests(SimpleTestCase):
    """Проверить основные и динамические URL проекта."""

    def test_homepage_uses_real_project_data(self) -> None:
        response = self.client.get(reverse("homepage:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "homepage/index.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "Гарантийные документы под контролем")
        self.assertContains(response, "Действующих гарантий")

    def test_warranty_list_displays_sqlite_rows(self) -> None:
        response = self.client.get(reverse("warranties:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "warranties/warranty_list.html")
        self.assertIsInstance(response.context["documents"][0], sqlite3.Row)
        self.assertContains(response, "Ноутбук Lenovo IdeaPad 3")
        self.assertContains(response, "WRT-2026-001")
        self.assertContains(response, "Всего документов: 2")

    def test_warranty_detail_uses_dynamic_url(self) -> None:
        response = self.client.get(reverse("warranties:detail", args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "warranties/warranty_detail.html")
        self.assertContains(response, "Иванов Иван Иванович")
        self.assertContains(response, "ООО «ТехноМир»")

    def test_unknown_warranty_returns_404(self) -> None:
        response = self.client.get(reverse("warranties:detail", args=[999]))
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Документ не найден", status_code=404)

    def test_client_list_displays_related_objects(self) -> None:
        response = self.client.get(reverse("clients:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "clients/client_list.html")
        self.assertContains(response, "Петрова Анна Сергеевна")

    def test_client_detail_displays_related_warranty(self) -> None:
        response = self.client.get(reverse("clients:detail", args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "clients/client_detail.html")
        self.assertContains(response, "WRT-2026-001")

    def test_warranty_list_handles_empty_collection(self) -> None:
        connection = MagicMock()
        connection.execute.return_value.fetchall.return_value = []
        with patch(
            "warranties.views.get_connection",
            return_value=connection,
        ):
            response = self.client.get(reverse("warranties:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Документов пока нет")
        connection.close.assert_called_once()

    def test_parameterized_warranty_search(self) -> None:
        response = self.client.get(
            reverse("warranties:search"),
            {"q": "Lenovo"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "warranties/warranty_search.html")
        self.assertContains(response, "WRT-2026-001")
        self.assertContains(response, "Найдено: 1")

    def test_search_does_not_interpret_query_as_sql(self) -> None:
        response = self.client.get(
            reverse("warranties:search"),
            {"q": "' OR 1=1 --"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Совпадений нет")
        self.assertContains(response, "Найдено: 0")
        self.assertNotContains(response, "Ноутбук Lenovo IdeaPad 3")

    def test_statistics_use_sql_aggregates(self) -> None:
        response = self.client.get(reverse("warranties:statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "warranties/statistics.html")
        self.assertContains(response, "Документы по статусам")
        self.assertContains(response, "Гарантия действует")
        self.assertContains(response, "Клиенты с несколькими документами")

    def test_unknown_client_returns_404(self) -> None:
        response = self.client.get(reverse("clients:detail", args=[999]))
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Клиент не найден", status_code=404)

    @override_settings(DEBUG=False)
    def test_custom_404_page(self) -> None:
        response = self.client.get("/unknown-address/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Страница не найдена", status_code=404)
        self.assertContains(response, "Вернуться на главную", status_code=404)

    def test_pages_include_bootstrap_and_accessible_navigation(self) -> None:
        response = self.client.get(reverse("homepage:index"))
        self.assertContains(response, "bootstrap@5.3.3")
        self.assertContains(response, 'href="#main-content"')
        self.assertContains(response, 'aria-label="Основная навигация"')
        self.assertContains(response, "/static/homepage/css/style.css")
        self.assertContains(response, "/static/homepage/js/main.js")
        self.assertContains(response, "/static/homepage/img/logo.svg")
        self.assertContains(response, 'id="current-year"')
        self.assertContains(response, reverse("warranties:statistics"))
