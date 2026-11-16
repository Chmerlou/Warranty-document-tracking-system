"""Django-модели гарантийных документов и связанных справочников."""

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Case, Value, When
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from unidecode import unidecode


class WarrantyDocumentQuerySet(models.QuerySet):
    """Повторно используемые выборки гарантийных документов."""

    def active(self):
        """Вернуть неаннулированные документы с неистёкшим сроком."""
        return self.filter(
            state=self.model.State.VALID,
            end_date__gte=timezone.localdate(),
        )

    def annulled(self):
        """Вернуть аннулированные документы."""
        return self.filter(state=self.model.State.ANNULLED)

    def expired(self):
        """Вернуть истёкшие, но не аннулированные документы."""
        return self.filter(
            state=self.model.State.VALID,
            end_date__lt=timezone.localdate(),
        )

    def ending_on(self, selected_date):
        """Вернуть документы, срок которых заканчивается в указанную дату."""
        return self.filter(end_date=selected_date)


class WarrantyDocumentManager(
    models.Manager.from_queryset(WarrantyDocumentQuerySet)
):
    """Менеджер документов с предметными методами QuerySet."""

    pass


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

    class State(models.TextChoices):
        VALID = "valid", "Действителен"
        ANNULLED = "annulled", "Аннулирован"

    doc_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Номер документа",
        help_text="Укажите уникальный номер с гарантийного документа.",
    )
    slug = models.SlugField(
        max_length=180,
        unique=True,
        editable=False,
        verbose_name="URL-идентификатор",
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
        help_text="Введите положительное количество полных месяцев.",
    )
    end_date = models.DateField(verbose_name="Дата окончания гарантии")
    state = models.CharField(
        max_length=12,
        choices=State.choices,
        default=State.VALID,
        verbose_name="Состояние документа",
    )
    is_extended_warranty = models.GeneratedField(
        expression=Case(
            When(warranty_months__gte=24, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Расширенная гарантия",
    )

    objects = WarrantyDocumentManager()

    def __str__(self) -> str:
        return f"{self.doc_number}: {self.product}"

    def save(self, *args, **kwargs) -> None:
        """Сформировать постоянный slug из номера документа и ID."""
        if self.slug:
            super().save(*args, **kwargs)
            return

        base_slug = slugify(unidecode(self.doc_number)) or "warranty"
        if self.pk:
            self.slug = f"{base_slug}-{self.pk}"
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = set(update_fields) | {"slug"}
            super().save(*args, **kwargs)
            return

        super().save(*args, **kwargs)
        self.slug = f"{base_slug}-{self.pk}"
        super().save(update_fields=["slug"])

    def get_absolute_url(self) -> str:
        """Вернуть адрес публичной карточки по slug."""
        return reverse("warranties:detail", kwargs={"slug": self.slug})

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
        if self.state == self.State.ANNULLED:
            return "Документ аннулирован"
        if self.days_left < 0:
            return "Гарантия истекла"
        if self.days_left == 0:
            return "Последний день гарантии"
        return "Гарантия действует"

    @property
    def expiration_notice(self) -> str:
        if self.state == self.State.ANNULLED:
            return "Документ аннулирован и не подтверждает гарантию."
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
