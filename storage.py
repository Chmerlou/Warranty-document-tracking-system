"""Загрузка объектов из JSON и сохранение объектов в JSON."""

import json
from pathlib import Path

from models import WarrantyDocument


def load_documents(file_path: Path) -> list[WarrantyDocument]:
    """Загрузить JSON и преобразовать записи в объекты документов."""
    if not file_path.exists():
        return []

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Не удалось прочитать файл {file_path}") from error

    if not isinstance(data, list):
        raise ValueError("JSON-файл должен содержать список документов")

    try:
        return [WarrantyDocument.from_dict(item) for item in data]
    except (TypeError, ValueError) as error:
        message = "JSON-файл содержит некорректный документ"
        raise ValueError(message) from error


def save_documents(
    file_path: Path,
    documents: list[WarrantyDocument],
) -> None:
    """Преобразовать объекты в словари и сохранить их в JSON."""
    data = [document.to_dict() for document in documents]
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        raise ValueError(f"Не удалось записать файл {file_path}") from error
