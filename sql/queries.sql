-- Проверенные запросы системы учета гарантийных документов

-- 1. Список гарантийных документов с сортировкой по номеру
SELECT id, doc_number, start_date, end_date
FROM warranty_documents
ORDER BY doc_number;

-- 2. Список клиентов в алфавитном порядке
SELECT id, name
FROM clients
ORDER BY name;

-- 3. Ближайшие по окончанию гарантии с ограничением выборки
SELECT id, doc_number, end_date
FROM warranty_documents
ORDER BY end_date
LIMIT 5;

-- 4. Действующие гарантии. В Django текущая дата вычисляется SQLite
SELECT id, doc_number, end_date
FROM warranty_documents
WHERE date(end_date) >= date('now', 'localtime')
ORDER BY end_date;

-- 5. Поиск документов по части названия товара
SELECT warranty_documents.id, warranty_documents.doc_number, products.name
FROM warranty_documents
JOIN products ON products.id = warranty_documents.product_id
WHERE lower(products.name) LIKE '%ноутбук%'
ORDER BY products.name;

-- 6. Документы, начавшие действовать в заданном диапазоне дат
SELECT id, doc_number, start_date
FROM warranty_documents
WHERE date(start_date) BETWEEN date('2026-01-01') AND date('2026-12-31')
ORDER BY start_date;

-- 7. Полные сведения о документах из четырех связанных таблиц
SELECT
    warranty_documents.id,
    warranty_documents.doc_number,
    clients.name AS client_name,
    products.name AS product_name,
    sellers.name AS seller_name,
    warranty_documents.end_date
FROM warranty_documents
JOIN clients ON clients.id = warranty_documents.client_id
JOIN products ON products.id = warranty_documents.product_id
JOIN sellers ON sellers.id = warranty_documents.seller_id
ORDER BY warranty_documents.end_date;

-- 8. Гарантийные документы выбранного клиента
SELECT
    warranty_documents.doc_number,
    products.name AS product_name,
    warranty_documents.end_date
FROM warranty_documents
JOIN products ON products.id = warranty_documents.product_id
WHERE warranty_documents.client_id = 1
ORDER BY warranty_documents.end_date;

-- 9. Карточка одного документа со связанными данными
SELECT
    warranty_documents.doc_number,
    clients.name AS client_name,
    products.name AS product_name,
    sellers.name AS seller_name
FROM warranty_documents
JOIN clients ON clients.id = warranty_documents.client_id
JOIN products ON products.id = warranty_documents.product_id
JOIN sellers ON sellers.id = warranty_documents.seller_id
WHERE warranty_documents.id = 1;

-- 10. Общие показатели реестра
SELECT
    COUNT(*) AS documents_count,
    COUNT(DISTINCT client_id) AS clients_count,
    ROUND(AVG(warranty_months), 1) AS average_months,
    MIN(end_date) AS nearest_end_date,
    MAX(end_date) AS latest_end_date
FROM warranty_documents;

-- 11. Количество документов по состоянию гарантии
SELECT
    CASE
        WHEN date(end_date) < date('now', 'localtime')
            THEN 'Гарантия истекла'
        WHEN date(end_date) = date('now', 'localtime')
            THEN 'Последний день гарантии'
        ELSE 'Гарантия действует'
    END AS status,
    COUNT(*) AS documents_count
FROM warranty_documents
GROUP BY status
ORDER BY documents_count DESC;

-- 12. Количество документов каждого клиента, включая клиентов без документов
SELECT
    clients.id,
    clients.name AS client_name,
    COUNT(warranty_documents.id) AS documents_count
FROM clients
LEFT JOIN warranty_documents
    ON warranty_documents.client_id = clients.id
GROUP BY clients.id, clients.name
ORDER BY documents_count DESC, clients.name;

-- 13. Продавцы с одной или несколькими зарегистрированными гарантиями
SELECT
    sellers.name AS seller_name,
    COUNT(warranty_documents.id) AS documents_count
FROM sellers
JOIN warranty_documents
    ON warranty_documents.seller_id = sellers.id
GROUP BY sellers.id, sellers.name
HAVING COUNT(warranty_documents.id) >= 1
ORDER BY documents_count DESC, sellers.name;

-- 14. Клиенты с несколькими гарантийными документами
SELECT
    clients.name AS client_name,
    COUNT(warranty_documents.id) AS documents_count
FROM clients
JOIN warranty_documents
    ON warranty_documents.client_id = clients.id
GROUP BY clients.id, clients.name
HAVING COUNT(warranty_documents.id) > 1
ORDER BY documents_count DESC, clients.name;
