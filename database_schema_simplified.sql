-- ===================================================================
-- Упрощенная система управления логистикой и доставкой
-- SQL схема базы данных (PostgreSQL)
-- ===================================================================

DROP TABLE IF EXISTS delivery CASCADE;
DROP TABLE IF EXISTS shipment CASCADE;
DROP TABLE IF EXISTS order_item CASCADE;
DROP TABLE IF EXISTS route CASCADE;
DROP TABLE IF EXISTS warehouse CASCADE;
DROP TABLE IF EXISTS driver CASCADE;
DROP TABLE IF EXISTS vehicle CASCADE;
DROP TABLE IF EXISTS customer CASCADE;
DROP TABLE IF EXISTS employee CASCADE;

-- ===================================================================
-- 1. ТАБЛИЦА: Сотрудник
-- ===================================================================
CREATE TABLE employee (
    employee_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    position VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    hire_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- ===================================================================
-- 2. ТАБЛИЦА: Клиент
-- ===================================================================
CREATE TABLE customer (
    customer_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- ===================================================================
-- 3. ТАБЛИЦА: Водитель
-- ===================================================================
CREATE TABLE driver (
    driver_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL UNIQUE,
    license_number VARCHAR(20) UNIQUE NOT NULL,
    experience_years INT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
);

-- ===================================================================
-- 4. ТАБЛИЦА: Транспортное средство
-- ===================================================================
CREATE TABLE vehicle (
    vehicle_id SERIAL PRIMARY KEY,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    capacity_kg DECIMAL(10, 2) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE
);

-- ===================================================================
-- 5. ТАБЛИЦА: Склад
-- ===================================================================
CREATE TABLE warehouse (
    warehouse_id SERIAL PRIMARY KEY,
    warehouse_name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    manager_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (manager_id) REFERENCES employee(employee_id)
);

-- ===================================================================
-- 6. ТАБЛИЦА: Маршрут доставки
-- ===================================================================
CREATE TABLE route (
    route_id SERIAL PRIMARY KEY,
    route_name VARCHAR(255) NOT NULL,
    start_location VARCHAR(255) NOT NULL,
    end_location VARCHAR(255) NOT NULL,
    distance_km DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- ===================================================================
-- 7. ТАБЛИЦА: Заказ
-- ===================================================================
CREATE TABLE order_item (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    order_date DATE NOT NULL,
    delivery_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    cost DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id)
);

-- ===================================================================
-- 8. ТАБЛИЦА: Партия доставки
-- ===================================================================
CREATE TABLE shipment (
    shipment_id SERIAL PRIMARY KEY,
    shipment_number VARCHAR(50) UNIQUE NOT NULL,
    order_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    driver_id INT NOT NULL,
    route_id INT NOT NULL,
    departure_time TIMESTAMP,
    arrival_time TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    cost DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES order_item(order_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicle(vehicle_id),
    FOREIGN KEY (driver_id) REFERENCES driver(driver_id),
    FOREIGN KEY (route_id) REFERENCES route(route_id)
);

-- ===================================================================
-- 9. ТАБЛИЦА: Доставка
-- ===================================================================
CREATE TABLE delivery (
    delivery_id SERIAL PRIMARY KEY,
    shipment_id INT NOT NULL,
    recipient_name VARCHAR(255) NOT NULL,
    recipient_phone VARCHAR(20) NOT NULL,
    recipient_address VARCHAR(255) NOT NULL,
    delivery_time TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (shipment_id) REFERENCES shipment(shipment_id)
);

-- ===================================================================
-- ИНДЕКСЫ для оптимизации запросов
-- ===================================================================
CREATE INDEX idx_order_customer ON order_item(customer_id);
CREATE INDEX idx_order_status ON order_item(status);
CREATE INDEX idx_shipment_vehicle ON shipment(vehicle_id);
CREATE INDEX idx_shipment_driver ON shipment(driver_id);
CREATE INDEX idx_shipment_status ON shipment(status);
CREATE INDEX idx_delivery_shipment ON delivery(shipment_id);

COMMIT;
