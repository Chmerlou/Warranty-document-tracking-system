"""Класс клиента системы."""

from .party import Party


class Client(Party):
    """Владелец товара и гарантийного документа."""

    def role_name(self) -> str:
        """Вернуть название роли клиента."""
        return "Клиент"
