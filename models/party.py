"""Базовый класс участника гарантийных отношений."""


class Party:
    """Общий участник предметной области с идентификатором и именем."""

    def __init__(self, party_id: int, name: str) -> None:
        """Создать участника и проверить переданные данные."""
        self._id = self.validate_id(party_id)
        self._name = self.validate_name(name)

    @staticmethod
    def validate_id(party_id: int) -> int:
        """Проверить и вернуть положительный идентификатор."""
        if party_id <= 0:
            raise ValueError("Идентификатор должен быть положительным")
        return party_id

    @staticmethod
    def validate_name(name: str) -> str:
        """Проверить и вернуть непустое имя участника."""
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Имя не может быть пустым")
        return normalized_name

    @property
    def id(self) -> int:
        """Вернуть идентификатор участника."""
        return self._id

    @property
    def name(self) -> str:
        """Вернуть имя участника."""
        return self._name

    def role_name(self) -> str:
        """Вернуть название роли для полиморфного представления."""
        return "Участник"

    def to_dict(self) -> dict[str, object]:
        """Преобразовать участника в данные для JSON."""
        return {"id": self.id, "name": self.name}

    def __str__(self) -> str:
        """Вернуть удобное строковое представление участника."""
        return f"{self.role_name()}: {self.name}"
