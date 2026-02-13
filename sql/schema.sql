-- Core SQL schema for AI Store Assistant (MVP)

CREATE TABLE stores (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  name TEXT NOT NULL,
  timezone TEXT NOT NULL DEFAULT 'UTC',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  store_id TEXT NOT NULL,
  business_date DATE NOT NULL,
  order_ts TIMESTAMP,
  gross_sales NUMERIC(12,2) NOT NULL DEFAULT 0,
  discounts NUMERIC(12,2) NOT NULL DEFAULT 0,
  net_sales NUMERIC(12,2) NOT NULL DEFAULT 0,
  channel TEXT,
  FOREIGN KEY (store_id) REFERENCES stores(id)
);

CREATE TABLE order_items (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  order_id TEXT NOT NULL,
  item_name TEXT NOT NULL,
  quantity NUMERIC(10,2) NOT NULL DEFAULT 1,
  line_net_sales NUMERIC(12,2) NOT NULL DEFAULT 0,
  FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE inventory_snapshots (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  store_id TEXT NOT NULL,
  sku TEXT NOT NULL,
  snapshot_date DATE NOT NULL,
  on_hand_qty NUMERIC(12,3) NOT NULL DEFAULT 0,
  unit_cost NUMERIC(10,4) NOT NULL DEFAULT 0,
  waste_qty NUMERIC(12,3) NOT NULL DEFAULT 0,
  FOREIGN KEY (store_id) REFERENCES stores(id)
);

CREATE TABLE staff_shifts (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  store_id TEXT NOT NULL,
  staff_id TEXT NOT NULL,
  shift_date DATE NOT NULL,
  start_ts TIMESTAMP,
  end_ts TIMESTAMP,
  labor_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
  FOREIGN KEY (store_id) REFERENCES stores(id)
);

CREATE TABLE daily_financials (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  store_id TEXT NOT NULL,
  business_date DATE NOT NULL,
  net_sales NUMERIC(12,2) NOT NULL DEFAULT 0,
  labor_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
  waste_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
  cogs NUMERIC(12,2) NOT NULL DEFAULT 0,
  gross_profit NUMERIC(12,2) NOT NULL DEFAULT 0,
  UNIQUE (tenant_id, store_id, business_date),
  FOREIGN KEY (store_id) REFERENCES stores(id)
);

-- Useful index pattern for tenant isolation + daily query performance
CREATE INDEX idx_orders_tenant_store_date ON orders(tenant_id, store_id, business_date);
CREATE INDEX idx_daily_financials_tenant_store_date ON daily_financials(tenant_id, store_id, business_date);
