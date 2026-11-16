"""Модели клиентов гарантийного реестра."""

from django.db import models


class Client(models.Model):
    """Владелец товара и связанных гарантийных документов."""

    name = models.CharField(
        max_length=200,
        verbose_name="ФИО клиента",
        help_text="Укажите полное имя владельца гарантийного документа.",
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
