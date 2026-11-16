"""Главная страница и общий HTML-каркас Django-приложения."""

from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.html import escape

from storage import load_documents
from warranty_documents import get_unique_clients

DATA_FILE = Path(settings.BASE_DIR) / "data" / "warranty_documents.json"


def _nav_link(href: str, label: str, active_path: str) -> str:
    """Сформировать доступную ссылку основной навигации."""
    is_active = href == active_path
    css_class = "site-nav__link is-active" if is_active else "site-nav__link"
    current = ' aria-current="page"' if is_active else ""
    return (
        f'<a class="{css_class}" href="{href}"{current}>'
        f"{label}</a>"
    )


def page(title: str, content: str, active_path: str = "") -> str:
    """Собрать единый HTML-документ с Bootstrap и локальными стилями."""
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/"
        "dist/css/bootstrap.min.css"
    )
    navigation = "".join(
        (
            _nav_link("/", "Главная", active_path),
            _nav_link("/warranties/", "Гарантии", active_path),
            _nav_link("/clients/", "Клиенты", active_path),
        )
    )
    styles = """
    :root {
        color-scheme: light dark;
        --canvas: #f4f7f6;
        --surface: #fbfdfc;
        --surface-strong: #e7eeeb;
        --ink: #18231f;
        --muted: #52615b;
        --line: #cbd7d2;
        --accent: #0f766e;
        --accent-strong: #0b5e58;
        --focus: #d97706;
        --success-bg: #dff3e9;
        --success-text: #155b3b;
        --warning-bg: #fff0cf;
        --warning-text: #795000;
        --danger-bg: #fde6e4;
        --danger-text: #8b2c25;
        --radius: 12px;
        --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
    }
    * { box-sizing: border-box; }
    body {
        margin: 0;
        background: var(--canvas);
        color: var(--ink);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.55;
    }
    a { color: var(--accent); }
    a:focus-visible {
        outline: 3px solid var(--focus);
        outline-offset: 3px;
        border-radius: 4px;
    }
    .skip-link {
        position: fixed;
        top: 8px;
        left: 8px;
        z-index: 10;
        padding: 10px 14px;
        border-radius: 8px;
        background: var(--ink);
        color: var(--surface);
        transform: translateY(-160%);
    }
    .skip-link:focus { transform: translateY(0); }
    .site-header {
        border-bottom: 1px solid var(--line);
        background: var(--surface);
    }
    .site-header__inner {
        width: min(1120px, calc(100% - 32px));
        min-height: 72px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
    }
    .brand {
        color: var(--ink);
        font-size: 1.08rem;
        font-weight: 750;
        letter-spacing: -0.02em;
        text-decoration: none;
    }
    .site-nav { display: flex; align-items: center; gap: 4px; }
    .site-nav__link {
        min-height: 44px;
        padding: 10px 14px;
        display: inline-flex;
        align-items: center;
        border-radius: 8px;
        color: var(--muted);
        font-weight: 650;
        text-decoration: none;
        transition: background-color 180ms var(--ease-out),
                    color 180ms var(--ease-out),
                    transform 180ms var(--ease-out);
    }
    .site-nav__link.is-active {
        background: var(--surface-strong);
        color: var(--ink);
    }
    .site-nav__link:active { transform: scale(0.98); }
    main {
        width: min(1120px, calc(100% - 32px));
        min-height: calc(100dvh - 144px);
        margin: 0 auto;
        padding: 48px 0 64px;
    }
    h1, h2, h3 {
        letter-spacing: -0.025em;
        line-height: 1.15;
        text-wrap: balance;
    }
    h1 { max-width: 20ch; margin-bottom: 16px; font-weight: 760; }
    p { max-width: 70ch; text-wrap: pretty; }
    .lead-copy { color: var(--muted); font-size: 1.1rem; }
    .page-heading { margin-bottom: 32px; }
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 16px;
        margin: 32px 0 40px;
    }
    .summary-item {
        padding: 20px;
        border: 1px solid var(--line);
        border-radius: var(--radius);
        background: var(--surface);
    }
    .summary-item__value {
        display: block;
        font-size: 1.75rem;
        font-weight: 760;
        line-height: 1.2;
    }
    .summary-item__label { color: var(--muted); }
    .action-row { display: flex; flex-wrap: wrap; gap: 12px; }
    .button-link {
        min-height: 44px;
        padding: 10px 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--accent);
        border-radius: 9px;
        background: var(--accent);
        color: #f7fffd;
        font-weight: 700;
        text-decoration: none;
        transition: background-color 180ms var(--ease-out),
                    transform 180ms var(--ease-out);
    }
    .button-link--secondary {
        background: transparent;
        color: var(--accent);
    }
    .button-link:active { transform: scale(0.98); }
    .record-list {
        margin: 0;
        padding: 0;
        border-top: 1px solid var(--line);
        list-style: none;
    }
    .record-list__link {
        min-height: 76px;
        padding: 18px 4px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        border-bottom: 1px solid var(--line);
        color: var(--ink);
        text-decoration: none;
        transition: color 180ms var(--ease-out),
                    transform 180ms var(--ease-out);
    }
    .record-list__title { display: block; font-weight: 720; }
    .record-list__meta { color: var(--muted); font-size: 0.94rem; }
    .status-badge {
        flex: 0 0 auto;
        padding: 5px 9px;
        border-radius: 7px;
        font-size: 0.82rem;
        font-weight: 720;
    }
    .status-badge--success {
        background: var(--success-bg);
        color: var(--success-text);
    }
    .status-badge--warning {
        background: var(--warning-bg);
        color: var(--warning-text);
    }
    .status-badge--danger {
        background: var(--danger-bg);
        color: var(--danger-text);
    }
    .detail-panel {
        padding: 28px;
        border: 1px solid var(--line);
        border-radius: var(--radius);
        background: var(--surface);
    }
    .detail-list {
        display: grid;
        grid-template-columns: minmax(150px, 0.6fr) 1.4fr;
        gap: 0;
        margin: 0 0 28px;
    }
    .detail-list dt, .detail-list dd {
        margin: 0;
        padding: 13px 0;
        border-bottom: 1px solid var(--line);
    }
    .detail-list dt { color: var(--muted); font-weight: 620; }
    .empty-state, .error-state {
        max-width: 680px;
        padding: 28px;
        border: 1px solid var(--line);
        border-radius: var(--radius);
        background: var(--surface);
    }
    .error-state { border-color: var(--danger-text); }
    .site-footer {
        min-height: 72px;
        padding: 20px 16px;
        border-top: 1px solid var(--line);
        color: var(--muted);
        text-align: center;
    }
    @media (hover: hover) and (pointer: fine) {
        .site-nav__link:hover { background: var(--surface-strong); }
        .button-link:hover { background: var(--accent-strong); }
        .button-link--secondary:hover {
            background: var(--surface-strong);
            color: var(--accent-strong);
        }
        .record-list__link:hover {
            color: var(--accent-strong);
            transform: translateX(3px);
        }
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --canvas: #101714;
            --surface: #17211d;
            --surface-strong: #22302a;
            --ink: #edf5f1;
            --muted: #b4c3bc;
            --line: #35463f;
            --accent: #5eead4;
            --accent-strong: #99f6e4;
            --focus: #fbbf24;
            --success-bg: #153d2d;
            --success-text: #a7f3d0;
            --warning-bg: #46350e;
            --warning-text: #fde68a;
            --danger-bg: #4b211f;
            --danger-text: #fecaca;
        }
        .button-link { color: #0b2823; }
        .button-link--secondary { color: var(--accent); }
    }
    @media (max-width: 640px) {
        .site-header__inner {
            padding: 12px 0;
            align-items: flex-start;
            flex-direction: column;
            gap: 8px;
        }
        .site-nav {
            width: 100%;
            overflow-x: auto;
            padding-bottom: 2px;
        }
        main { padding-top: 32px; }
        .record-list__link { align-items: flex-start; flex-direction: column; }
        .detail-list { grid-template-columns: 1fr; }
        .detail-list dt { padding-bottom: 2px; border-bottom: 0; }
        .detail-list dd { padding-top: 2px; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
        }
    }
    """
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="color-scheme" content="light dark">
    <title>{escape(title)}</title>
    <link rel="stylesheet" href="{bootstrap}">
    <style>{styles}</style>
</head>
<body>
    <a class="skip-link" href="#main-content">К содержанию</a>
    <header class="site-header">
        <div class="site-header__inner">
            <a class="brand" href="/">Гарантийный реестр</a>
            <nav class="site-nav" aria-label="Основная навигация">
                {navigation}
            </nav>
        </div>
    </header>
    <main id="main-content">{content}</main>
    <footer class="site-footer">Учебный проект на Django 5.2</footer>
</body>
</html>"""


def index(request: HttpRequest) -> HttpResponse:
    """Показать главную страницу с показателями реальных данных."""
    try:
        documents = load_documents(DATA_FILE)
    except ValueError as error:
        content = f"""
        <section class="error-state" role="alert">
            <h1>Данные временно недоступны</h1>
            <p>{escape(error)}</p>
        </section>
        """
        return HttpResponse(page("Ошибка данных", content, "/"), status=500)

    active_count = sum(
        document.get_status() != "Гарантия истекла"
        for document in documents
    )
    clients_count = len(get_unique_clients(documents))
    content = f"""
    <section class="page-heading">
        <h1>Гарантийные документы под контролем</h1>
        <p class="lead-copy">
            Просматривайте документы, сроки и связанные данные клиентов
            в едином веб-интерфейсе.
        </p>
    </section>
    <section class="summary-grid" aria-label="Сводка реестра">
        <div class="summary-item">
            <span class="summary-item__value">{len(documents)}</span>
            <span class="summary-item__label">Документов</span>
        </div>
        <div class="summary-item">
            <span class="summary-item__value">{active_count}</span>
            <span class="summary-item__label">Действующих гарантий</span>
        </div>
        <div class="summary-item">
            <span class="summary-item__value">{clients_count}</span>
            <span class="summary-item__label">Клиентов</span>
        </div>
    </section>
    <div class="action-row">
        <a class="button-link" href="/warranties/">
            Открыть реестр гарантий
        </a>
        <a class="button-link button-link--secondary" href="/clients/">
            Посмотреть клиентов
        </a>
    </div>
    """
    return HttpResponse(page("Гарантийный реестр", content, "/"))


def page_not_found(
    request: HttpRequest,
    exception: Exception,
) -> HttpResponse:
    """Показать оформленную страницу для неизвестного адреса."""
    content = """
    <section class="error-state">
        <h1>Страница не найдена</h1>
        <p>Проверьте адрес или вернитесь к разделам реестра.</p>
        <a class="button-link" href="/">Вернуться на главную</a>
    </section>
    """
    return HttpResponse(page("Страница не найдена", content), status=404)
