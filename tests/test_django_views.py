"""Тесты маршрутов и view-функций Django-приложения."""

from django.test import SimpleTestCase, override_settings
from django.urls import reverse


class WebPageTests(SimpleTestCase):
    """Проверить основные и динамические URL проекта."""

    def test_homepage_uses_real_project_data(self) -> None:
        response = self.client.get(reverse("homepage:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Гарантийные документы под контролем")
        self.assertContains(response, "Действующих гарантий")

    def test_warranty_list_displays_json_objects(self) -> None:
        response = self.client.get(reverse("warranties:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ноутбук Lenovo IdeaPad 3")
        self.assertContains(response, "WRT-2026-001")

    def test_warranty_detail_uses_dynamic_url(self) -> None:
        response = self.client.get(reverse("warranties:detail", args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Иванов Иван Иванович")
        self.assertContains(response, "ООО «ТехноМир»")

    def test_unknown_warranty_returns_404(self) -> None:
        response = self.client.get(reverse("warranties:detail", args=[999]))
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Документ не найден", status_code=404)

    def test_client_list_displays_related_objects(self) -> None:
        response = self.client.get(reverse("clients:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Петрова Анна Сергеевна")

    def test_client_detail_displays_related_warranty(self) -> None:
        response = self.client.get(reverse("clients:detail", args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "WRT-2026-001")

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
