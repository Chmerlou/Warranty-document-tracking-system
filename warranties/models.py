"""Django-модели гарантийных документов и связанных справочников."""

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Product(models.Model):
    """Товар, на который распространяется гарантия."""

    name = models.CharField(max_length=200, verbose_name="Название товара")

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Seller(models.Model):
    """Организация, продавшая товар."""

    name = models.CharField(max_length=200, verbose_name="Продавец")

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "Продавец"
        verbose_name_plural = "Продавцы"


class WarrantyDocument(models.Model):
    """Документ, связывающий клиента, товар, продавца и срок гарантии."""

    doc_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Номер документа",
    )
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.PROTECT,
        related_name="warranty_documents",
        verbose_name="Клиент",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="warranty_documents",
        verbose_name="Товар",
    )
    seller = models.ForeignKey(
        Seller,
        on_delete=models.PROTECT,
        related_name="warranty_documents",
        verbose_name="Продавец",
    )
    start_date = models.DateField(verbose_name="Дата начала гарантии")
    warranty_months = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Срок гарантии в месяцах",
    )
    end_date = models.DateField(verbose_name="Дата окончания гарантии")

    def __str__(self) -> str:
        return f"{self.doc_number}: {self.product}"

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def client_name(self) -> str:
        return self.client.name

    @property
    def seller_name(self) -> str:
        return self.seller.name

    @property
    def start_date_display(self) -> str:
        return self.start_date.strftime("%d.%m.%Y")

    @property
    def end_date_display(self) -> str:
        return self.end_date.strftime("%d.%m.%Y")

    @property
    def days_left(self) -> int:
        return (self.end_date - timezone.localdate()).days

    @property
    def status(self) -> str:
        if self.days_left < 0:
            return "Гарантия истекла"
        if self.days_left == 0:
            return "Последний день гарантии"
        return "Гарантия действует"

    @property
    def expiration_notice(self) -> str:
        if self.days_left < 0:
            return f"Гарантия истекла {abs(self.days_left)} дн. назад."
        if self.days_left == 0:
            return "Гарантия заканчивается сегодня."
        return f"До окончания гарантии осталось {self.days_left} дн."

    class Meta:
        ordering = ["end_date", "doc_number"]
        verbose_name = "Гарантийный документ"
        verbose_name_plural = "Гарантийные документы"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(warranty_months__gt=0),
                name="warranty_months_positive",
            ),
        ]
