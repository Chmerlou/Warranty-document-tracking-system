"""Класс товара, на который распространяется гарантия."""


class Product:
    """Товар с идентификатором и наименованием."""

    def __init__(self, product_id: int, name: str) -> None:
        """Создать товар и проверить его данные."""
        if product_id <= 0:
            raise ValueError("Идентификатор товара должен быть положительным")
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Название товара не может быть пустым")
        self._id = product_id
        self._name = normalized_name

    @property
    def id(self) -> int:
        """Вернуть идентификатор товара."""
        return self._id

    @property
    def name(self) -> str:
        """Вернуть название товара."""
        return self._name

    def to_dict(self) -> dict[str, object]:
        """Преобразовать товар в данные для JSON."""
        return {"id": self.id, "name": self.name}

    def __str__(self) -> str:
        """Вернуть удобное строковое представление товара."""
        return f"Товар: {self.name}"
