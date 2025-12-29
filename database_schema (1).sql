-- PostgreSQL 15 Database Schema for Logistics Management System
-- No order_number and shipment_number columns!

DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;

-- 1. EMPLOYEES
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    position VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    hire_date DATE NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. CUSTOMERS
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    postal_code VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. DRIVERS
CREATE TABLE drivers (
    driver_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL UNIQUE,
    license_number VARCHAR(20) UNIQUE NOT NULL,
    license_expiry_date DATE NOT NULL,
    experience_years INT NOT NULL,
    rating DECIMAL(3, 2) DEFAULT 5.00,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- 4. VEHICLES
CREATE TABLE vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    capacity_kg DECIMAL(10, 2) NOT NULL,
    capacity_cubic_m DECIMAL(10, 2) NOT NULL,
    mileage INT DEFAULT 0,
    last_maintenance DATE,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. WAREHOUSES
CREATE TABLE warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    warehouse_name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    postal_code VARCHAR(10),
    manager_id INT,
    capacity_items INT NOT NULL,
    current_items INT DEFAULT 0,
    phone VARCHAR(20),
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL
);

-- 6. DELIVERY ROUTES
CREATE TABLE delivery_routes (
    route_id SERIAL PRIMARY KEY,
    route_name VARCHAR(255) NOT NULL,
    start_location VARCHAR(255) NOT NULL,
    end_location VARCHAR(255) NOT NULL,
    distance_km DECIMAL(10, 2) NOT NULL,
    estimated_duration_hours DECIMAL(5, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. ORDERS
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    order_date DATE NOT NULL,
    delivery_date DATE NOT NULL,
    description VARCHAR(500),
    total_weight_kg DECIMAL(10, 2),
    total_volume_cubic_m DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'Ожидает',
    priority VARCHAR(20) DEFAULT 'Обычная',
    cost DECIMAL(10, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT
);

-- 8. SHIPMENTS
CREATE TABLE shipments (
    shipment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    driver_id INT NOT NULL,
    route_id INT NOT NULL,
    departure_time TIMESTAMP,
    expected_arrival_time TIMESTAMP,
    actual_arrival_time TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Ожидает',
    distance_traveled_km DECIMAL(10, 2),
    fuel_consumed_liters DECIMAL(10, 2),
    cost DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE RESTRICT,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id) ON DELETE RESTRICT,
    FOREIGN KEY (route_id) REFERENCES delivery_routes(route_id) ON DELETE RESTRICT
);

-- 9. DELIVERIES
CREATE TABLE deliveries (
    delivery_id SERIAL PRIMARY KEY,
    shipment_id INT NOT NULL,
    recipient_name VARCHAR(255) NOT NULL,
    recipient_phone VARCHAR(20) NOT NULL,
    recipient_address VARCHAR(255) NOT NULL,
    recipient_city VARCHAR(100) NOT NULL,
    delivery_time TIMESTAMP,
    signature_required BOOLEAN DEFAULT FALSE,
    signature_obtained BOOLEAN DEFAULT FALSE,
    signature_date TIMESTAMP,
    delivery_notes TEXT,
    status VARCHAR(50) DEFAULT 'В пути',
    attempts INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id) ON DELETE CASCADE
);

-- UPDATE TIMESTAMP TRIGGER
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER orders_update_timestamp
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER shipments_update_timestamp
BEFORE UPDATE ON shipments
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER deliveries_update_timestamp
BEFORE UPDATE ON deliveries
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- INDEXES
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_delivery_date ON orders(delivery_date);
CREATE INDEX idx_shipments_order ON shipments(order_id);
CREATE INDEX idx_shipments_vehicle ON shipments(vehicle_id);
CREATE INDEX idx_shipments_driver ON shipments(driver_id);
CREATE INDEX idx_shipments_status ON shipments(status);
CREATE INDEX idx_deliveries_shipment ON deliveries(shipment_id);
CREATE INDEX idx_deliveries_status ON deliveries(status);
CREATE INDEX idx_customers_city ON customers(city);
CREATE INDEX idx_warehouses_city ON warehouses(city);

-- VIEWS
CREATE VIEW order_statistics AS
SELECT
    COUNT(*) as total_orders,
    COUNT(CASE WHEN status = 'Доставлено' THEN 1 END) as delivered_orders,
    COUNT(CASE WHEN status = 'В пути' THEN 1 END) as in_transit_orders,
    ROUND(AVG(cost)::NUMERIC, 2) as avg_order_cost,
    SUM(cost) as total_revenue
FROM orders;

CREATE VIEW driver_activity AS
SELECT
    d.driver_id,
    e.full_name,
    COUNT(s.shipment_id) as total_shipments,
    AVG(d.rating) as avg_rating,
    COUNT(CASE WHEN s.status = 'Доставлено' THEN 1 END) as delivered_shipments
FROM drivers d
JOIN employees e ON d.employee_id = e.employee_id
LEFT JOIN shipments s ON d.driver_id = s.driver_id
GROUP BY d.driver_id, e.full_name;

CREATE VIEW warehouse_occupancy AS
SELECT
    w.warehouse_id,
    w.warehouse_name,
    w.capacity_items,
    w.current_items,
    ROUND(w.current_items::NUMERIC / w.capacity_items * 100, 2) as occupancy_percent
FROM warehouses w;

CREATE VIEW shipments_with_orders AS
SELECT
    s.shipment_id,
    s.order_id,
    o.customer_id,
    c.contact_person,
    c.company_name,
    v.license_plate,
    e.full_name as driver_name,
    s.status,
    s.cost,
    s.created_at
FROM shipments s
JOIN orders o ON s.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN vehicles v ON s.vehicle_id = v.vehicle_id
JOIN drivers d ON s.driver_id = d.driver_id
JOIN employees e ON d.employee_id = e.employee_id;

-- CHECK TABLES
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
SELECT viewname FROM pg_views WHERE schemaname = 'public' ORDER BY viewname;
