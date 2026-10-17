-- One answer to chapters 03 to 06. CI runs `python -m shop --indexes solutions/indexes.sql check`.
CREATE INDEX orders_customer_created ON orders (customer_id, created_at);
CREATE INDEX orders_status_created ON orders (status, created_at, total_cents);
CREATE INDEX orders_created ON orders (created_at);
CREATE INDEX customers_country ON customers (country);
