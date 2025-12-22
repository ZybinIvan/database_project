-- ===================================================================
-- Примеры аналитических SQL запросов
-- Информационная система управления логистикой и доставкой
-- ===================================================================

-- ===================================================================
-- 1. СТАТИСТИКА ПО ЗАКАЗАМ
-- ===================================================================

-- Количество заказов по статусам
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM orders
GROUP BY status
ORDER BY count DESC;

-- Заказы по приоритетам с суммой стоимости
SELECT 
    priority,
    COUNT(*) as order_count,
    SUM(cost) as total_cost,
    ROUND(AVG(cost), 2) as avg_cost
FROM orders
GROUP BY priority
ORDER BY total_cost DESC;

-- Заказы за последние 30 дней
SELECT 
    order_number,
    o.company_name,
    order_date,
    delivery_date,
    status,
    cost
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY order_date DESC;

-- ===================================================================
-- 2. СТАТИСТИКА ПО ДОСТАВКАМ
-- ===================================================================

-- Количество доставок по статусам с временем в пути
SELECT 
    status,
    COUNT(*) as delivery_count,
    ROUND(AVG(EXTRACT(EPOCH FROM (actual_arrival_time - departure_time)) / 3600), 2) as avg_hours
FROM shipments
WHERE departure_time IS NOT NULL
GROUP BY status;

-- Средний расход топлива по типам транспорта
SELECT 
    v.vehicle_type,
    COUNT(s.shipment_id) as shipments,
    ROUND(AVG(s.fuel_consumed_liters), 2) as avg_fuel,
    ROUND(AVG(s.distance_traveled_km), 2) as avg_distance
FROM shipments s
JOIN vehicles v ON s.vehicle_id = v.vehicle_id
WHERE s.fuel_consumed_liters IS NOT NULL
GROUP BY v.vehicle_type
ORDER BY avg_fuel DESC;

-- Скорость доставки (часов) по маршрутам
SELECT 
    dr.route_name,
    COUNT(s.shipment_id) as deliveries,
    ROUND(AVG(EXTRACT(EPOCH FROM (s.actual_arrival_time - s.departure_time)) / 3600), 2) as avg_hours,
    ROUND(AVG(dr.distance_km), 2) as distance_km
FROM shipments s
JOIN delivery_routes dr ON s.route_id = dr.route_id
WHERE s.actual_arrival_time IS NOT NULL
GROUP BY dr.route_name, dr.distance_km
ORDER BY avg_hours DESC;

-- ===================================================================
-- 3. ФИНАНСОВАЯ АНАЛИТИКА
-- ===================================================================

-- Доход по месяцам
SELECT 
    DATE_TRUNC('month', order_date)::DATE as month,
    COUNT(*) as order_count,
    SUM(cost) as total_revenue,
    ROUND(AVG(cost), 2) as avg_order_value
FROM orders
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month DESC;

-- Доход по клиентам (TOP 10)
SELECT 
    c.company_name,
    COUNT(o.order_id) as order_count,
    SUM(o.cost) as total_spent,
    ROUND(AVG(o.cost), 2) as avg_order
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.company_name
ORDER BY total_spent DESC
LIMIT 10;

-- Затраты на доставку по отношению к доходу
SELECT 
    DATE_TRUNC('month', o.order_date)::DATE as month,
    SUM(o.cost) as revenue,
    SUM(s.cost) as shipment_costs,
    ROUND(SUM(s.cost) / SUM(o.cost) * 100, 2) as cost_percentage
FROM orders o
LEFT JOIN shipments s ON o.order_id = s.order_id
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month DESC;

-- ===================================================================
-- 4. АНАЛИЗ ВОДИТЕЛЕЙ
-- ===================================================================

-- Производительность водителей
SELECT 
    e.full_name,
    d.rating,
    COUNT(s.shipment_id) as deliveries,
    ROUND(AVG(s.distance_traveled_km), 2) as avg_distance,
    ROUND(AVG(s.cost), 2) as avg_shipment_cost,
    CASE 
        WHEN d.rating >= 4.8 THEN 'Excellent'
        WHEN d.rating >= 4.5 THEN 'Good'
        WHEN d.rating >= 4.0 THEN 'Average'
        ELSE 'Poor'
    END as performance
FROM drivers d
JOIN employees e ON d.employee_id = e.employee_id
LEFT JOIN shipments s ON d.driver_id = s.driver_id
GROUP BY d.driver_id, e.full_name, d.rating
ORDER BY d.rating DESC;

-- Количество завершенных доставок по водителям
SELECT 
    e.full_name,
    COUNT(CASE WHEN s.status = 'Delivered' THEN 1 END) as completed,
    COUNT(CASE WHEN s.status IN ('Pending', 'In Transit') THEN 1 END) as in_progress,
    COUNT(CASE WHEN s.status = 'Failed' THEN 1 END) as failed
FROM drivers d
JOIN employees e ON d.employee_id = e.employee_id
LEFT JOIN shipments s ON d.driver_id = s.driver_id
GROUP BY d.driver_id, e.full_name
ORDER BY completed DESC;

-- ===================================================================
-- 5. АНАЛИЗ ПАРКА ТРАНСПОРТА
-- ===================================================================

-- Загруженность транспорта
SELECT 
    v.license_plate,
    v.vehicle_type,
    v.brand,
    v.model,
    COUNT(s.shipment_id) as shipments,
    ROUND(AVG(s.distance_traveled_km), 2) as avg_distance,
    v.mileage as total_mileage,
    CASE 
        WHEN v.is_available THEN 'Available'
        ELSE 'Unavailable'
    END as status
FROM vehicles v
LEFT JOIN shipments s ON v.vehicle_id = s.vehicle_id
GROUP BY v.vehicle_id, v.license_plate, v.vehicle_type, v.brand, v.model, v.mileage, v.is_available
ORDER BY shipments DESC;

-- Требующие обслуживания транспортные средства
SELECT 
    license_plate,
    vehicle_type,
    brand,
    model,
    mileage,
    last_maintenance,
    CASE 
        WHEN last_maintenance IS NULL OR last_maintenance < CURRENT_DATE - INTERVAL '3 months' THEN 'Требуется'
        ELSE 'OK'
    END as maintenance_status
FROM vehicles
ORDER BY last_maintenance ASC NULLS FIRST;

-- ===================================================================
-- 6. АНАЛИЗ СКЛАДОВ
-- ===================================================================

-- Заполненность складов
SELECT 
    warehouse_name,
    city,
    current_items,
    capacity_items,
    ROUND((current_items::NUMERIC / NULLIF(capacity_items, 0)) * 100, 2) as occupancy_percent,
    CASE 
        WHEN current_items::NUMERIC / capacity_items >= 0.9 THEN 'Full'
        WHEN current_items::NUMERIC / capacity_items >= 0.5 THEN 'Half-Full'
        ELSE 'Low'
    END as level
FROM warehouses
ORDER BY occupancy_percent DESC;

-- Эффективность складов (заказов через каждый)
SELECT 
    w.warehouse_name,
    COUNT(o.order_id) as total_orders,
    SUM(o.cost) as total_revenue,
    ROUND(AVG(o.cost), 2) as avg_order_cost
FROM warehouses w
LEFT JOIN orders o ON w.warehouse_id = o.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name
ORDER BY total_orders DESC;

-- ===================================================================
-- 7. АНАЛИЗ ДОСТАВОК И КЛИЕНТОВ
-- ===================================================================

-- Успешность доставок (процент выполненных)
SELECT 
    COUNT(CASE WHEN status = 'Delivered' THEN 1 END) as successful,
    COUNT(CASE WHEN status = 'Failed' THEN 1 END) as failed,
    ROUND(
        COUNT(CASE WHEN status = 'Delivered' THEN 1 END)::NUMERIC / 
        COUNT(*)::NUMERIC * 100, 2
    ) as success_rate
FROM deliveries;

-- Лучшие маршруты по стабильности
SELECT 
    dr.route_name,
    COUNT(s.shipment_id) as total_shipments,
    COUNT(CASE WHEN s.status = 'Delivered' THEN 1 END) as delivered,
    ROUND(
        COUNT(CASE WHEN s.status = 'Delivered' THEN 1 END)::NUMERIC / 
        COUNT(s.shipment_id)::NUMERIC * 100, 2
    ) as delivery_rate,
    ROUND(AVG(s.distance_traveled_km), 2) as avg_distance_km
FROM shipments s
JOIN delivery_routes dr ON s.route_id = dr.route_id
GROUP BY dr.route_id, dr.route_name
ORDER BY delivery_rate DESC;

-- Среднее время доставки до городов
SELECT 
    d.recipient_city,
    COUNT(d.delivery_id) as deliveries,
    ROUND(
        AVG(EXTRACT(EPOCH FROM (d.delivery_time - s.departure_time)) / 3600), 2
    ) as avg_hours,
    ROUND(
        AVG(EXTRACT(EPOCH FROM (d.delivery_time - s.departure_time)) / 86400), 2
    ) as avg_days
FROM deliveries d
JOIN shipments s ON d.shipment_id = s.shipment_id
WHERE d.delivery_time IS NOT NULL AND s.departure_time IS NOT NULL
GROUP BY d.recipient_city
ORDER BY avg_hours DESC;

-- ===================================================================
-- 8. КОМПЛЕКСНАЯ СТАТИСТИКА
-- ===================================================================

-- Дашборд: KPI
SELECT 
    'Total Orders' as metric,
    COUNT(*)::TEXT as value
FROM orders
UNION ALL
SELECT 
    'Delivered Orders',
    COUNT(*)::TEXT
FROM orders
WHERE status = 'Delivered'
UNION ALL
SELECT 
    'Total Revenue (₽)',
    ROUND(SUM(cost))::TEXT
FROM orders
UNION ALL
SELECT 
    'Average Order Cost (₽)',
    ROUND(AVG(cost))::TEXT
FROM orders
UNION ALL
SELECT 
    'Active Drivers',
    COUNT(*)::TEXT
FROM drivers
WHERE is_available = TRUE
UNION ALL
SELECT 
    'Total Shipments',
    COUNT(*)::TEXT
FROM shipments;

-- Детальный отчет по заказам
SELECT 
    o.order_number,
    c.company_name as customer,
    o.order_date,
    o.delivery_date,
    o.status,
    o.priority,
    o.cost,
    COUNT(s.shipment_id) as shipments,
    STRING_AGG(DISTINCT e.full_name, ', ') as drivers,
    STRING_AGG(DISTINCT v.license_plate, ', ') as vehicles
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN shipments s ON o.order_id = s.order_id
LEFT JOIN drivers d ON s.driver_id = d.driver_id
LEFT JOIN employees e ON d.employee_id = e.employee_id
LEFT JOIN vehicles v ON s.vehicle_id = v.vehicle_id
GROUP BY o.order_id, o.order_number, c.company_name, o.order_date, o.delivery_date, o.status, o.priority, o.cost
ORDER BY o.order_date DESC;

-- ===================================================================
-- 9. ЭКСПОРТИРУЕМЫЕ ПРЕДСТАВЛЕНИЯ
-- ===================================================================

-- Для Tableau/Power BI: Fact Table доставок
SELECT 
    s.shipment_id,
    o.order_number,
    c.company_name,
    d.recipient_city,
    dr.route_name,
    e.full_name as driver_name,
    v.brand as vehicle_brand,
    s.departure_time,
    s.actual_arrival_time,
    s.status,
    s.distance_traveled_km,
    s.fuel_consumed_liters,
    s.cost as shipment_cost,
    o.cost as order_cost
FROM shipments s
JOIN orders o ON s.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN drivers d_driver ON s.driver_id = d_driver.driver_id
JOIN employees e ON d_driver.employee_id = e.employee_id
JOIN vehicles v ON s.vehicle_id = v.vehicle_id
JOIN delivery_routes dr ON s.route_id = dr.route_id
LEFT JOIN deliveries d ON s.shipment_id = d.shipment_id;
