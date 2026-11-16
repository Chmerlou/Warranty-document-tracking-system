"""Переиспользуемые SQL-фрагменты для Django-представлений."""

DOCUMENT_FIELDS = """
    SELECT
        warranty_documents.id,
        warranty_documents.doc_number,
        warranty_documents.client_id,
        clients.name AS client_name,
        products.name AS product_name,
        sellers.name AS seller_name,
        warranty_documents.start_date,
        warranty_documents.end_date,
        strftime(
            '%d.%m.%Y', warranty_documents.start_date
        ) AS start_date_display,
        strftime(
            '%d.%m.%Y', warranty_documents.end_date
        ) AS end_date_display,
        warranty_documents.warranty_months,
        CASE
            WHEN date(warranty_documents.end_date) < date(
                'now', 'localtime'
            ) THEN 'Гарантия истекла'
            WHEN date(warranty_documents.end_date) = date(
                'now', 'localtime'
            ) THEN 'Последний день гарантии'
            ELSE 'Гарантия действует'
        END AS status,
        MAX(
            CAST(
                julianday(warranty_documents.end_date)
                - julianday(date('now', 'localtime'))
                AS INTEGER
            ),
            0
        ) AS days_left,
        CASE
            WHEN date(warranty_documents.end_date) < date(
                'now', 'localtime'
            ) THEN 'Уведомление: гарантия уже истекла'
            WHEN date(warranty_documents.end_date) = date(
                'now', 'localtime'
            ) THEN 'Уведомление: сегодня последний день гарантии!'
            WHEN julianday(warranty_documents.end_date)
                - julianday(date('now', 'localtime')) <= 30
            THEN 'Уведомление: гарантия истекает в течение месяца!'
            ELSE 'Гарантия в порядке, уведомлений нет'
        END AS expiration_notice
    FROM warranty_documents
    JOIN clients ON clients.id = warranty_documents.client_id
    JOIN products ON products.id = warranty_documents.product_id
    JOIN sellers ON sellers.id = warranty_documents.seller_id
"""
