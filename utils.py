"""Вспомогательные функции безопасного пользовательского ввода."""

from datetime import date
from typing import Optional


def input_non_empty(prompt: str) -> str:
    """Запрашивать строку, пока пользователь не введет непустое значение."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Значение не может быть пустым.")


def input_int(
    prompt: str,
    minimum: Optional[int] = None,
    maximum: Optional[int] = None,
) -> int:
    """Безопасно запросить целое число в допустимом диапазоне."""
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Введите целое число.")
            continue

        if minimum is not None and value < minimum:
            print(f"Число должно быть не меньше {minimum}.")
            continue
        if maximum is not None and value > maximum:
            print(f"Число должно быть не больше {maximum}.")
            continue
        return value


def input_date(prompt: str) -> date:
    """Безопасно запросить дату в формате ГГГГ-ММ-ДД."""
    while True:
        raw_value = input(prompt).strip()
        try:
            return date.fromisoformat(raw_value)
        except ValueError:
            print("Введите корректную дату в формате ГГГГ-ММ-ДД.")
