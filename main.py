"""Консольный интерфейс системы учета гарантийных документов."""

from pathlib import Path

from storage import load_documents, save_documents
from utils import input_date, input_int, input_non_empty
from warranty_documents import (
    create_warranty_document,
    delete_warranty_document,
    filter_documents_by_status,
    filter_expiring_documents,
    find_warranty_documents,
    show_warranty_documents,
    sort_warranty_documents,
)

DATA_FILE = Path(__file__).parent / "data" / "warranty_documents.json"


def print_menu() -> None:
    """Вывести главное меню приложения."""
    print("\n===== Учет гарантийных документов =====")
    print("1. Показать все документы")
    print("2. Добавить документ")
    print("3. Найти документ")
    print("4. Отфильтровать документы по статусу")
    print("5. Показать гарантии, истекающие в течение 30 дней")
    print("6. Отсортировать документы по дате окончания")
    print("7. Удалить документ")
    print("0. Сохранить данные и выйти")


def add_document_from_input(documents: list[dict]) -> None:
    """Получить данные документа от пользователя и добавить его."""
    doc_number = input_non_empty("Номер документа: ")
    client_name = input_non_empty("Клиент: ")
    product_name = input_non_empty("Товар: ")
    seller = input_non_empty("Продавец: ")
    start_date = input_date("Дата начала гарантии (ГГГГ-ММ-ДД): ")
    warranty_months = input_int("Срок гарантии в месяцах: ", 1)

    try:
        document = create_warranty_document(
            documents,
            doc_number,
            client_name,
            product_name,
            seller,
            start_date,
            warranty_months,
        )
    except ValueError as error:
        print(f"Документ не добавлен: {error}")
        return

    print(f"Документ {document['doc_number']} добавлен.")


def search_documents(documents: list[dict]) -> None:
    """Найти и вывести документы по поисковому запросу."""
    query = input_non_empty("Введите номер, клиента, товар или продавца: ")
    show_warranty_documents(find_warranty_documents(documents, query))


def show_documents_by_status(documents: list[dict]) -> None:
    """Вывести документы с выбранным статусом гарантии."""
    statuses = {
        1: "Гарантия действует",
        2: "Последний день гарантии",
        3: "Гарантия истекла",
    }
    print("1. Гарантия действует")
    print("2. Последний день гарантии")
    print("3. Гарантия истекла")
    choice = input_int("Выберите статус: ", 1, 3)
    show_warranty_documents(
        filter_documents_by_status(documents, statuses[choice])
    )


def remove_document(documents: list[dict]) -> None:
    """Удалить документ по его номеру."""
    doc_number = input_non_empty("Номер удаляемого документа: ")
    if delete_warranty_document(documents, doc_number):
        print("Документ удален.")
    else:
        print("Документ с таким номером не найден.")


def load_project_data() -> list[dict]:
    """Загрузить данные, не завершая приложение при ошибке файла."""
    try:
        return load_documents(DATA_FILE)
    except ValueError as error:
        print(f"Предупреждение: {error}")
        print("Приложение запущено с пустым списком документов.")
        return []


def main() -> None:
    """Запустить интерактивный цикл приложения."""
    documents = load_project_data()

    while True:
        print_menu()
        choice = input_int("Выберите действие: ", 0, 7)

        if choice == 0:
            try:
                save_documents(DATA_FILE, documents)
            except ValueError as error:
                print(f"Не удалось сохранить данные: {error}")
                continue
            print("Данные сохранены. Работа завершена.")
            break
        if choice == 1:
            show_warranty_documents(documents)
        elif choice == 2:
            add_document_from_input(documents)
        elif choice == 3:
            search_documents(documents)
        elif choice == 4:
            show_documents_by_status(documents)
        elif choice == 5:
            show_warranty_documents(filter_expiring_documents(documents, 30))
        elif choice == 6:
            show_warranty_documents(sort_warranty_documents(documents))
        elif choice == 7:
            remove_document(documents)


if __name__ == "__main__":
    main()
