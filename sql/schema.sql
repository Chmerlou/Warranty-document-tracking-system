-- Система учета гарантийных документов: структура базы данных

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (trim(name) <> '')
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (trim(name) <> '')
);

CREATE TABLE IF NOT EXISTS sellers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (trim(name) <> '')
);

CREATE TABLE IF NOT EXISTS warranty_documents (
    id INTEGER PRIMARY KEY,
    doc_number TEXT NOT NULL UNIQUE CHECK (trim(doc_number) <> ''),
    client_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    seller_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    warranty_months INTEGER NOT NULL CHECK (warranty_months > 0),
    end_date TEXT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (seller_id) REFERENCES sellers(id)
);

CREATE INDEX IF NOT EXISTS idx_warranty_documents_client
ON warranty_documents(client_id);

CREATE INDEX IF NOT EXISTS idx_warranty_documents_end_date
ON warranty_documents(end_date);
