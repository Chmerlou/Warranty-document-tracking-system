"""Класс продавца товара."""

from .party import Party


class Seller(Party):
    """Организация, продавшая товар по гарантии."""

    def role_name(self) -> str:
        """Вернуть название роли продавца."""
        return "Продавец"
