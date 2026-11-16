"""Загрузка и сохранение данных приложения в формате JSON."""

import json
from pathlib import Path
from typing import Any


def load_documents(file_path: Path) -> list[dict[str, Any]]:
    """Загрузить список документов из JSON-файла."""
    if not file_path.exists():
        return []

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Не удалось прочитать файл {file_path}") from error

    if not isinstance(data, list):
        raise ValueError("JSON-файл должен содержать список документов")
    if not all(isinstance(document, dict) for document in data):
        raise ValueError("Каждый документ в JSON-файле должен быть объектом")
    return data


def save_documents(
    file_path: Path,
    documents: list[dict[str, Any]],
) -> None:
    """Сохранить документы в JSON-файл с поддержкой русского текста."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(documents, file, ensure_ascii=False, indent=2)
    except OSError as error:
        raise ValueError(f"Не удалось записать файл {file_path}") from error
