"""Веб-страницы гарантийных документов."""

from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.html import escape

from homepage.views import page
from storage import load_documents
from warranty_documents import find_warranty_document_by_id

DATA_FILE = Path(settings.BASE_DIR) / "data" / "warranty_documents.json"


def _status_badge(status: str) -> str:
    """Сформировать статусный бейдж с единым словарем состояний."""
    classes = {
        "Гарантия действует": "status-badge--success",
        "Последний день гарантии": "status-badge--warning",
        "Гарантия истекла": "status-badge--danger",
    }
    css_class = classes.get(status, "status-badge--warning")
    return (
        f'<span class="status-badge {css_class}">'
        f"{escape(status)}</span>"
    )


def _data_error(error: ValueError) -> HttpResponse:
    """Вернуть понятное состояние ошибки загрузки данных."""
    content = f"""
    <section class="error-state" role="alert">
        <h1>Не удалось загрузить документы</h1>
        <p>{escape(error)}</p>
        <a class="button-link" href="/">Вернуться на главную</a>
    </section>
    """
    return HttpResponse(
        page("Ошибка данных", content, "/warranties/"),
        status=500,
    )


def warranty_list(request: HttpRequest) -> HttpResponse:
    """Показать список объектов WarrantyDocument из JSON."""
    try:
        documents = load_documents(DATA_FILE)
    except ValueError as error:
        return _data_error(error)

    if documents:
        items = "".join(
            f"""
            <li>
                <a class="record-list__link"
                   href="/warranties/{document.id}/">
                    <span>
                        <span class="record-list__title">
                            {escape(document.product.name)}
                        </span>
                        <span class="record-list__meta">
                            {escape(document.doc_number)} ·
                            {escape(document.client.name)}
                        </span>
                    </span>
                    {_status_badge(document.get_status())}
                </a>
            </li>
            """
            for document in documents
        )
        body = f'<ul class="record-list">{items}</ul>'
    else:
        body = """
        <section class="empty-state">
            <h2>Документов пока нет</h2>
            <p>Добавьте первую запись через консольную версию приложения.</p>
        </section>
        """

    content = f"""
    <section class="page-heading">
        <h1>Гарантийные документы</h1>
        <p class="lead-copy">
            Реестр товаров, клиентов, продавцов и сроков гарантии.
        </p>
    </section>
    {body}
    """
    return HttpResponse(
        page("Гарантийные документы", content, "/warranties/")
    )


def warranty_detail(
    request: HttpRequest,
    document_id: int,
) -> HttpResponse:
    """Показать объект гарантийного документа по динамическому URL."""
    try:
        documents = load_documents(DATA_FILE)
    except ValueError as error:
        return _data_error(error)

    document = find_warranty_document_by_id(documents, document_id)
    if document is None:
        content = """
        <section class="error-state">
            <h1>Документ не найден</h1>
            <p>В реестре нет гарантийного документа с таким ID.</p>
            <a class="button-link" href="/warranties/">
                Вернуться к документам
            </a>
        </section>
        """
        return HttpResponse(
            page("Документ не найден", content, "/warranties/"),
            status=404,
        )

    status = document.get_status()
    content = f"""
    <section class="page-heading">
        <h1>{escape(document.product.name)}</h1>
        <p class="lead-copy">
            Документ {escape(document.doc_number)}
        </p>
    </section>
    <section class="detail-panel">
        <dl class="detail-list">
            <dt>Статус</dt>
            <dd>{_status_badge(status)}</dd>
            <dt>Клиент</dt>
            <dd>
                <a href="/clients/{document.client.id}/">
                    {escape(document.client.name)}
                </a>
            </dd>
            <dt>Продавец</dt>
            <dd>{escape(document.seller.name)}</dd>
            <dt>Дата начала</dt>
            <dd>{document.start_date:%d.%m.%Y}</dd>
            <dt>Дата окончания</dt>
            <dd>{document.end_date:%d.%m.%Y}</dd>
            <dt>Срок гарантии</dt>
            <dd>{document.warranty_months} мес.</dd>
            <dt>Осталось дней</dt>
            <dd>{document.days_until_expiration()}</dd>
        </dl>
        <p>{escape(document.get_expiration_notice())}</p>
        <a class="button-link button-link--secondary" href="/warranties/">
            Вернуться к документам
        </a>
    </section>
    """
    return HttpResponse(
        page(document.doc_number, content, "/warranties/")
    )
