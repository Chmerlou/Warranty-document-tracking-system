"""Класс гарантийного документа и его предметное поведение."""

import calendar
from datetime import date
from typing import Any, Optional

from .client import Client
from .product import Product
from .seller import Seller


class WarrantyDocument:
    """Гарантийный документ, связывающий клиента, товар и продавца."""

    def __init__(
        self,
        document_id: int,
        doc_number: str,
        client: Client,
        product: Product,
        seller: Seller,
        start_date: date,
        warranty_months: int,
    ) -> None:
        """Создать гарантийный документ и рассчитать дату окончания."""
        if document_id <= 0:
            message = "Идентификатор документа должен быть положительным"
            raise ValueError(message)
        normalized_number = doc_number.strip()
        if not normalized_number:
            raise ValueError("Номер документа не может быть пустым")

        self._id = document_id
        self._doc_number = normalized_number
        self._client = client
        self._product = product
        self._seller = seller
        self._start_date = start_date
        self._warranty_months = self.validate_warranty_months(warranty_months)
        self._end_date = self.calculate_end_date(
            start_date,
            self._warranty_months,
        )

    @staticmethod
    def validate_warranty_months(months: int) -> int:
        """Проверить и вернуть положительный срок гарантии."""
        if months <= 0:
            raise ValueError("Срок гарантии должен быть положительным")
        return months

    @staticmethod
    def calculate_end_date(start_date: date, months: int) -> date:
        """Рассчитать дату окончания гарантии."""
        WarrantyDocument.validate_warranty_months(months)
        total_months = start_date.month + months - 1
        year = start_date.year + total_months // 12
        month = total_months % 12 + 1
        last_day = calendar.monthrange(year, month)[1]
        day = min(start_date.day, last_day)
        return date(year, month, day)

    @staticmethod
    def status_for_date(
        end_date: date,
        today: Optional[date] = None,
    ) -> str:
        """Определить статус по дате окончания гарантии."""
        current_date = today or date.today()
        if current_date > end_date:
            return "Гарантия истекла"
        if current_date == end_date:
            return "Последний день гарантии"
        return "Гарантия действует"

    @staticmethod
    def days_for_date(
        end_date: date,
        today: Optional[date] = None,
    ) -> int:
        """Определить число дней до указанной даты, но не меньше нуля."""
        current_date = today or date.today()
        return max((end_date - current_date).days, 0)

    @staticmethod
    def notice_for(days_left: int, status: str) -> str:
        """Сформировать уведомление по сроку и статусу гарантии."""
        if status == "Гарантия истекла":
            return "Уведомление: гарантия уже истекла"
        if days_left == 0:
            return "Уведомление: сегодня последний день гарантии!"
        if days_left <= 30:
            return "Уведомление: гарантия истекает в течение месяца!"
        return "Гарантия в порядке, уведомлений нет"

    @property
    def id(self) -> int:
        """Вернуть идентификатор документа."""
        return self._id

    @property
    def doc_number(self) -> str:
        """Вернуть номер документа."""
        return self._doc_number

    @property
    def client(self) -> Client:
        """Вернуть связанного клиента."""
        return self._client

    @property
    def product(self) -> Product:
        """Вернуть связанный товар."""
        return self._product

    @property
    def seller(self) -> Seller:
        """Вернуть связанного продавца."""
        return self._seller

    @property
    def start_date(self) -> date:
        """Вернуть дату начала гарантии."""
        return self._start_date

    @property
    def warranty_months(self) -> int:
        """Вернуть длительность гарантии в месяцах."""
        return self._warranty_months

    @property
    def end_date(self) -> date:
        """Вернуть рассчитанную дату окончания гарантии."""
        return self._end_date

    def get_status(self, today: Optional[date] = None) -> str:
        """Вернуть текущий статус этого документа."""
        return self.status_for_date(self.end_date, today)

    def days_until_expiration(self, today: Optional[date] = None) -> int:
        """Вернуть число дней до окончания этой гарантии."""
        return self.days_for_date(self.end_date, today)

    def get_expiration_notice(self, today: Optional[date] = None) -> str:
        """Сформировать уведомление для этого документа."""
        status = self.get_status(today)
        days_left = self.days_until_expiration(today)
        return self.notice_for(days_left, status)

    def expires_within(
        self,
        days: int,
        today: Optional[date] = None,
    ) -> bool:
        """Проверить, истекает ли действующая гарантия в заданный срок."""
        if days < 0:
            raise ValueError("Период отбора не может быть отрицательным")
        current_date = today or date.today()
        days_left = (self.end_date - current_date).days
        return 0 <= days_left <= days

    def matches(self, query: str) -> bool:
        """Проверить совпадение с номером, клиентом, товаром или продавцом."""
        normalized_query = query.strip().lower()
        values = (
            self.doc_number,
            self.client.name,
            self.product.name,
            self.seller.name,
        )
        return any(normalized_query in value.lower() for value in values)

    def to_dict(self) -> dict[str, object]:
        """Преобразовать объект и связанные сущности в данные для JSON."""
        return {
            "id": self.id,
            "doc_number": self.doc_number,
            "client": self.client.to_dict(),
            "product": self.product.to_dict(),
            "seller": self.seller.to_dict(),
            "start_date": self.start_date.isoformat(),
            "warranty_months": self.warranty_months,
            "end_date": self.end_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WarrantyDocument":
        """Создать объект из актуального или старого формата JSON."""
        try:
            document_id = int(data["id"])
            client = cls._client_from_data(data, document_id)
            product = cls._product_from_data(data, document_id)
            seller = cls._seller_from_data(data, document_id)
            return cls(
                document_id=document_id,
                doc_number=str(data["doc_number"]),
                client=client,
                product=product,
                seller=seller,
                start_date=date.fromisoformat(str(data["start_date"])),
                warranty_months=int(data["warranty_months"]),
            )
        except (KeyError, TypeError, ValueError) as error:
            message = "Некорректные данные гарантийного документа"
            raise ValueError(message) from error

    @staticmethod
    def _client_from_data(data: dict[str, Any], default_id: int) -> Client:
        """Создать клиента из нового или старого формата данных."""
        value = data.get("client")
        if isinstance(value, dict):
            return Client(int(value["id"]), str(value["name"]))
        return Client(default_id, str(data["client_name"]))

    @staticmethod
    def _product_from_data(data: dict[str, Any], default_id: int) -> Product:
        """Создать товар из нового или старого формата данных."""
        value = data.get("product")
        if isinstance(value, dict):
            return Product(int(value["id"]), str(value["name"]))
        return Product(default_id, str(data["product_name"]))

    @staticmethod
    def _seller_from_data(data: dict[str, Any], default_id: int) -> Seller:
        """Создать продавца из нового или старого формата данных."""
        value = data.get("seller")
        if isinstance(value, dict):
            return Seller(int(value["id"]), str(value["name"]))
        return Seller(default_id, str(data["seller"]))

    def __str__(self) -> str:
        """Вернуть полное строковое представление документа."""
        status = self.get_status()
        days_left = self.days_until_expiration()
        return (
            f"№ {self.doc_number} | {self.product.name}\n"
            f"{self.client} | {self.seller}\n"
            f"Гарантия: {self.start_date} - {self.end_date} | {status}\n"
            f"Осталось дней: {days_left}. "
            f"{self.get_expiration_notice()}"
        )
