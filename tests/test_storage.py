"""Тесты JSON-хранилища приложения."""

from pathlib import Path

import pytest

from storage import load_documents, save_documents


def test_save_and_load_documents(tmp_path: Path) -> None:
    file_path = tmp_path / "documents.json"
    documents = [{"id": 1, "doc_number": "WRT-001"}]
    save_documents(file_path, documents)
    assert load_documents(file_path) == documents


def test_load_missing_file_returns_empty_list(tmp_path: Path) -> None:
    assert load_documents(tmp_path / "missing.json") == []


def test_load_invalid_json_raises_clear_error(tmp_path: Path) -> None:
    file_path = tmp_path / "broken.json"
    file_path.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError, match="Не удалось прочитать"):
        load_documents(file_path)
