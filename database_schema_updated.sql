-- ===========================
-- СИСТЕМА УПРАВЛЕНИЯ ЛОГИСТИКОЙ
-- База данных PostgreSQL
-- ===========================

DROP TABLE IF EXISTS deliveries CASCADE;
DROP TABLE IF EXISTS shipments CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS delivery_routes CASCADE;
DROP TABLE IF EXISTS warehouses CASCADE;
DROP TABLE IF EXISTS drivers CASCADE;
DROP TABLE IF EXISTS vehicles CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS employees CASCADE;

-- 1. СОТРУДНИКИ
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

-- 2. КЛИЕНТЫ
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    postal_code VARCHAR(10),
    registration_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. ВОДИТЕЛИ
CREATE TABLE drivers (
    driver_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL UNIQUE,
    license_number VARCHAR(20) UNIQUE NOT NULL,
    license_expiry_date DATE NOT NULL,
    experience_years INT NOT NULL,
    rating DECIMAL(3, 2) DEFAULT 5.00,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- 4. ТРАНСПОРТНЫЕ СРЕДСТВА
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

-- 5. СКЛАДЫ
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
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

-- 6. МАРШРУТЫ ДОСТАВКИ
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

-- 7. ЗАКАЗЫ
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    order_date DATE NOT NULL,
    delivery_date DATE NOT NULL,
    description VARCHAR(500),
    total_weight_kg DECIMAL(10, 2),
    total_volume_cubic_m DECIMAL(10, 2),
    status VARCHAR(50) NOT NULL DEFAULT 'Ожидает',
    priority VARCHAR(20) DEFAULT 'Обычный',
    cost DECIMAL(10, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
);

-- 8. ПАРТИИ ДОСТАВКИ (SHIPMENTS)
CREATE TABLE shipments (
    shipment_id SERIAL PRIMARY KEY,
    shipment_number VARCHAR(50) UNIQUE NOT NULL,
    order_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    driver_id INT NOT NULL,
    route_id INT NOT NULL,
    departure_time TIMESTAMP,
    expected_arrival_time TIMESTAMP,
    actual_arrival_time TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Ожидает',
    distance_traveled_km DECIMAL(10, 2),
    fuel_consumed_liters DECIMAL(10, 2),
    cost DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
    FOREIGN KEY (route_id) REFERENCES delivery_routes(route_id)
);

-- 9. ДОСТАВКИ
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
    status VARCHAR(50) NOT NULL DEFAULT 'Ожидает',
    attempts INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
);

-- ===== ИНДЕКСЫ =====
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_delivery_date ON orders(delivery_date);
CREATE INDEX idx_shipments_vehicle ON shipments(vehicle_id);
CREATE INDEX idx_shipments_driver ON shipments(driver_id);
CREATE INDEX idx_shipments_status ON shipments(status);
CREATE INDEX idx_deliveries_shipment ON deliveries(shipment_id);
CREATE INDEX idx_deliveries_status ON deliveries(status);
CREATE INDEX idx_drivers_employee ON drivers(employee_id);

-- ===== ПРЕДСТАВЛЕНИЯ (VIEWS) =====

-- Статистика по заказам
CREATE VIEW order_statistics AS
SELECT 
    COUNT(*) as total_orders,
    COUNT(CASE WHEN status = 'Доставлено' THEN 1 END) as delivered_orders,
    COUNT(CASE WHEN status = 'В пути' THEN 1 END) as in_transit_orders,
    ROUND(AVG(cost)::NUMERIC, 2) as avg_order_cost,
    SUM(cost) as total_revenue
FROM orders;

-- Активность водителей
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

-- Загруженность складов
CREATE VIEW warehouse_occupancy AS
SELECT 
    w.warehouse_id,
    w.warehouse_name,
    w.current_items,
    w.capacity_items,
    ROUND(w.current_items::NUMERIC / NULLIF(w.capacity_items, 0) * 100, 2) as occupancy_percent
FROM warehouses w;

COMMIT;
