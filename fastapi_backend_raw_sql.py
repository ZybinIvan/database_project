from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date, timedelta
from typing import List, Optional
import logging
import os

app = FastAPI(
    title="Logistics Management System API",
    description="API для управления логистикой и доставкой",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://logistics:logistics_password@localhost:5432/logistics_db"
)

def get_db():
    """Получить подключение к БД"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def dict_from_cursor(cursor, row):
    """Преобразовать строку в словарь"""
    return dict(zip([desc[0] for desc in cursor.description], row))

def serialize_dates(obj):
    """Сериализация дат"""
    if isinstance(obj, (date, datetime)):
        return obj.strftime("%d.%m.%Y") if isinstance(obj, date) else obj.strftime("%d.%m.%Y %H:%M")
    return obj

def serialize_row(row):
    """Сериализовать строку с датами"""
    if isinstance(row, dict):
        return {k: serialize_dates(v) for k, v in row.items()}
    return row

# ============= EMPLOYEES =============

@app.get("/api/employees", tags=["Employees"])
def get_employees(skip: int = 0, limit: int = 100, conn = Depends(get_db)):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM employees WHERE is_active = true ORDER BY employee_id LIMIT %s OFFSET %s", 
                   (limit, skip))
        data = cur.fetchall()
        
        cur.execute("SELECT COUNT(*) FROM employees WHERE is_active = true")
        total = cur.fetchone()[0]
        
        return {"total": total, "data": [serialize_row(dict(r)) for r in data]}
    except Exception as e:
        logger.error(f"Ошибка получения сотрудников: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/employees", tags=["Employees"])
def create_employee(employee: dict, conn = Depends(get_db)):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO employees (full_name, position, email, phone, hire_date, salary)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING employee_id
        """, (employee["full_name"], employee["position"], employee["email"], 
              employee["phone"], employee.get("hire_date", date.today()), employee["salary"]))
        
        emp_id = cur.fetchone()[0]
        conn.commit()
        return {"id": emp_id, "message": "Сотрудник успешно создан"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка создания сотрудника: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= CUSTOMERS =============

@app.get("/api/customers", tags=["Customers"])
def get_customers(skip: int = 0, limit: int = 100, conn = Depends(get_db)):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT customer_id, company_name, contact_person, email, phone, city, 
                   address, postal_code, registration_date, is_active
            FROM customers
            WHERE is_active = true
            ORDER BY customer_id
            LIMIT %s OFFSET %s
        """, (limit, skip))
        data = cur.fetchall()
        
        cur.execute("SELECT COUNT(*) FROM customers WHERE is_active = true")
        total = cur.fetchone()[0]
        
        return {"total": total, "data": [serialize_row(dict(r)) for r in data]}
    except Exception as e:
        logger.error(f"Ошибка получения клиентов: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/customers", tags=["Customers"])
def create_customer(customer: dict, conn = Depends(get_db)):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO customers (company_name, contact_person, email, phone, city, address, postal_code, registration_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING customer_id
        """, (customer["company_name"], customer["contact_person"], customer.get("email"), 
              customer["phone"], customer["city"], customer["address"], 
              customer.get("postal_code"), customer.get("registration_date", date.today())))
        
        cust_id = cur.fetchone()[0]
        conn.commit()
        return {"id": cust_id, "message": "Клиент успешно создан"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка создания клиента: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}", tags=["Customers"])
def get_customer(customer_id: int, conn = Depends(get_db)):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cur.fetchone()
        if not customer:
            raise HTTPException(status_code=404, detail="Клиент не найден")
        return serialize_row(dict(customer))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения клиента: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= VEHICLES =============

@app.get("/api/vehicles", tags=["Vehicles"])
def get_vehicles(available_only: bool = False, conn = Depends(get_db)):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if available_only:
            cur.execute("""
                SELECT * FROM vehicles 
                WHERE is_available = true
                ORDER BY vehicle_id
            """)
        else:
            cur.execute("SELECT * FROM vehicles ORDER BY vehicle_id")
        
        data = cur.fetchall()
        
        if available_only:
            cur.execute("SELECT COUNT(*) FROM vehicles WHERE is_available = true")
        else:
            cur.execute("SELECT COUNT(*) FROM vehicles")
        total = cur.fetchone()[0]
        
        return {"total": total, "data": [serialize_row(dict(r)) for r in data]}
    except Exception as e:
        logger.error(f"Ошибка получения ТС: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vehicles", tags=["Vehicles"])
def create_vehicle(vehicle: dict, conn = Depends(get_db)):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO vehicles 
            (license_plate, vehicle_type, brand, model, year, capacity_kg, capacity_cubic_m, last_maintenance)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING vehicle_id
        """, (vehicle["license_plate"], vehicle["vehicle_type"], vehicle["brand"], 
              vehicle["model"], vehicle["year"], vehicle["capacity_kg"], 
              vehicle["capacity_cubic_m"], vehicle.get("last_maintenance", date.today())))
        
        veh_id = cur.fetchone()[0]
        conn.commit()
        return {"id": veh_id, "message": "Транспорт успешно добавлен"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка добавления ТС: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= DRIVERS =============

@app.get("/api/drivers", tags=["Drivers"])
def get_drivers(available_only: bool = False, conn = Depends(get_db)):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT d.driver_id, d.employee_id, e.full_name, d.license_number, 
                   d.license_expiry_date, d.experience_years, d.rating, d.is_available
            FROM drivers d
            JOIN employees e ON d.employee_id = e.employee_id
        """
        
        if available_only:
            query += " WHERE d.is_available = true"
        
        query += " ORDER BY d.driver_id"
        cur.execute(query)
        data = cur.fetchall()
        
        if available_only:
            cur.execute("SELECT COUNT(*) FROM drivers WHERE is_available = true")
        else:
            cur.execute("SELECT COUNT(*) FROM drivers")
        total = cur.fetchone()[0]
        
        return {"total": total, "data": [serialize_row(dict(r)) for r in data]}
    except Exception as e:
        logger.error(f"Ошибка получения водителей: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/drivers", tags=["Drivers"])
def create_driver(driver: dict, conn = Depends(get_db)):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO drivers 
            (employee_id, license_number, license_expiry_date, experience_years, rating)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING driver_id
        """, (driver["employee_id"], driver["license_number"], 
              driver["license_expiry_date"], driver["experience_years"], 
              driver.get("rating", 5.0)))
        
        drv_id = cur.fetchone()[0]
        conn.commit()
        return {"id": drv_id, "message": "Водитель успешно добавлен"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка добавления водителя: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/drivers/{driver_id}/availability", tags=["Drivers"])
def update_driver_availability(driver_id: int, is_available: bool, conn = Depends(get_db)):
    try:
        cur = conn.cursor()
        cur.execute("UPDATE drivers SET is_available = %s WHERE driver_id = %s", 
                   (is_available, driver_id))
        conn.commit()
        return {"message": f"Водитель доступен: {is_available}"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка обновления доступности: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= WAREHOUSES =============

@app.get("/api/warehouses", tags=["Warehouses"])
def get_warehouses(conn = Depends(get_db)):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT warehouse_id, warehouse_name, city, address, postal_code,
                   capacity_items, current_items, phone, email
            FROM warehouses
            WHERE is_active = true
            ORDER BY warehouse_id
        """)
        data = cur.fetchall()
        
        cur.execute("SELECT COUNT(*) FROM warehouses WHERE is_active = true")
        total = cur.fetchone()[0]
        
        return {"total": total, "data": [serialize_row(dict(r)) for r in data]}
    except Exception as e:
        logger.error(f"Ошибка получения складов: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= ORDERS =============

@app.get("/api/orders", tags=["Orders"])
def get_orders(status: Optional[str] = None, skip: int = 0, limit: int = 100, conn = Depends(get_db)):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT o.order_id, o.order_number, o.customer_id, c.contact_person as customer_name,
                   o.warehouse_id, o.order_date, o.delivery_date, o.total_weight_kg,
                   o.total_volume_cubic_m, o.status, o.priority, o.cost, o.notes
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            WHERE 1=1
        """
        
        params = []
        if status:
            query += " AND o.status = %s"
            params.append(status)
        
        query += " ORDER BY o.order_id DESC LIMIT %s OFFSET %s"
        params.extend([limit, skip])
        
        cur.execute(query, params)
        data = cur.fetchall()
        
        count_query = "SELECT COUNT(*) FROM orders WHERE 1=1"
        count_params = []
        if status:
            count_query += " AND status = %s"
            count_params.append(status)
        
        cur.execute(count_query, count_params)
        total = cur.fetchone()[0]
        
        return {"total": total, "data": [serialize_row(dict(r)) for r in data]}
    except Exception as e:
        logger.error(f"Ошибка получения заказов: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orders", tags=["Orders"])
def create_order(order: dict, conn = Depends(get_db)):
    try:
        cur = conn.cursor()
        
        # Получить последний ID и создать номер
        cur.execute("SELECT COALESCE(MAX(order_id), 0) + 1 as next_id FROM orders")
        next_id = cur.fetchone()[0]
        
        cur.execute("""
            INSERT INTO orders 
            (order_id, order_number, customer_id, warehouse_id, order_date, 
             delivery_date, total_weight_kg, total_volume_cubic_m, status, priority, cost, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING order_id
        """, (next_id, str(next_id), order["customer_id"], order.get("warehouse_id", 1),
              order.get("order_date", date.today()), order["delivery_date"],
              order.get("total_weight_kg"), order.get("total_volume_cubic_m"),
              order.get("status", "Ожидает"), order.get("priority", "Обычный"),
              order["cost"], order.get("notes")))
        
        order_id = cur.fetchone()[0]
        conn.commit()
        return {"id": order_id, "message": "Заказ успешно создан"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка создания заказа: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/{order_id}", tags=["Orders"])
def get_order(order_id: int, conn = Depends(get_db)):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT o.order_id, o.order_number, o.customer_id, c.contact_person as customer_name,
                   o.warehouse_id, o.order_date, o.delivery_date, o.total_weight_kg,
                   o.total_volume_cubic_m, o.status, o.priority, o.cost, o.notes
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = %s
        """, (order_id,))
        order = cur.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")
        return serialize_row(dict(order))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения заказа: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/orders/{order_id}", tags=["Orders"])
def update_order(order_id: int, order: dict, conn = Depends(get_db)):
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE orders 
            SET customer_id = %s, warehouse_id = %s, delivery_date = %s, 
                total_weight_kg = %s, total_volume_cubic_m = %s, status = %s, 
                priority = %s, cost = %s, notes = %s, updated_at = NOW()
            WHERE order_id = %s
        """, (order.get("customer_id"), order.get("warehouse_id"), order.get("delivery_date"),
              order.get("total_weight_kg"), order.get("total_volume_cubic_m"),
              order.get("status"), order.get("priority"), order.get("cost"),
              order.get("notes"), order_id))
        conn.commit()
        return {"message": "Заказ обновлен"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка обновления заказа: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/orders/{order_id}/status", tags=["Orders"])
def update_order_status(order_id: int, status: str, conn = Depends(get_db)):
    try:
        cur = conn.cursor()
        cur.execute("UPDATE orders SET status = %s, updated_at = NOW() WHERE order_id = %s",
                   (status, order_id))
        conn.commit()
        return {"message": f"Статус заказа обновлен на {status}"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка обновления статуса: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= SHIPMENTS =============

@app.get("/api/shipments", tags=["Shipments"])
def get_shipments(status: Optional[str] = None, conn = Depends(get_db)):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT s.shipment_id, s.shipment_number, s.order_id, o.order_number as order_number,
                   s.vehicle_id, v.license_plate, s.driver_id, e.full_name as driver_name,
                   s.route_id, dr.route_name, s.departure_time, s.expected_arrival_time,
                   s.actual_arrival_time, s.status, s.distance_traveled_km, 
                   s.fuel_consumed_liters, s.cost
            FROM shipments s
            LEFT JOIN orders o ON s.order_id = o.order_id
            LEFT JOIN vehicles v ON s.vehicle_id = v.vehicle_id
            LEFT JOIN drivers d ON s.driver_id = d.driver_id
            LEFT JOIN employees e ON d.employee_id = e.employee_id
            LEFT JOIN delivery_routes dr ON s.route_id = dr.route_id
            WHERE 1=1
        """
        
        params = []
        if status:
            query += " AND s.status = %s"
            params.append(status)
        
        query += " ORDER BY s.shipment_id DESC"
        cur.execute(query, params)
        data = cur.fetchall()
        
        count_query = "SELECT COUNT(*) FROM shipments WHERE 1=1"
        count_params = []
        if status:
            count_query += " AND status = %s"
            count_params.append(status)
        
        cur.execute(count_query, count_params)
        total = cur.fetchone()[0]
        
        return {"total": total, "data": [serialize_row(dict(r)) for r in data]}
    except Exception as e:
        logger.error(f"Ошибка получения доставок: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/shipments", tags=["Shipments"])
def create_shipment(shipment: dict, conn = Depends(get_db)):
    try:
        cur = conn.cursor()
        
        # Получить последний ID и создать номер
        cur.execute("SELECT COALESCE(MAX(shipment_id), 0) + 1 as next_id FROM shipments")
        next_id = cur.fetchone()[0]
        
        cur.execute("""
            INSERT INTO shipments 
            (shipment_id, shipment_number, order_id, vehicle_id, driver_id, route_id, status, cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING shipment_id
        """, (next_id, str(next_id), shipment["order_id"], shipment["vehicle_id"],
              shipment["driver_id"], shipment["route_id"],
              shipment.get("status", "Ожидает"), shipment["cost"]))
        
        shipment_id = cur.fetchone()[0]
        conn.commit()
        return {"id": shipment_id, "message": "Доставка успешно создана"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка создания доставки: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/shipments/{shipment_id}/status", tags=["Shipments"])
def update_shipment_status(shipment_id: int, status: str, conn = Depends(get_db)):
    try:
        cur = conn.cursor()
        
        update_query = "UPDATE shipments SET status = %s, updated_at = NOW()"
        params = [status]
        
        if status == "В пути":
            update_query += ", departure_time = NOW()"
        elif status == "Доставлено":
            update_query += ", actual_arrival_time = NOW()"
        
        update_query += " WHERE shipment_id = %s"
        params.append(shipment_id)
        
        cur.execute(update_query, params)
        conn.commit()
        return {"message": f"Статус доставки обновлен на {status}"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка обновления статуса доставки: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= DELIVERIES =============

@app.get("/api/deliveries", tags=["Deliveries"])
def get_deliveries(status: Optional[str] = None, conn = Depends(get_db)):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT del.delivery_id, del.shipment_id, s.shipment_number, del.recipient_name,
                   del.recipient_phone, del.recipient_address, del.recipient_city,
                   del.delivery_time, del.signature_required, del.signature_obtained,
                   del.status, del.attempts
            FROM deliveries del
            LEFT JOIN shipments s ON del.shipment_id = s.shipment_id
            WHERE 1=1
        """
        
        params = []
        if status:
            query += " AND del.status = %s"
            params.append(status)
        
        query += " ORDER BY del.delivery_id DESC"
        cur.execute(query, params)
        data = cur.fetchall()
        
        count_query = "SELECT COUNT(*) FROM deliveries WHERE 1=1"
        count_params = []
        if status:
            count_query += " AND status = %s"
            count_params.append(status)
        
        cur.execute(count_query, count_params)
        total = cur.fetchone()[0]
        
        return {"total": total, "data": [serialize_row(dict(r)) for r in data]}
    except Exception as e:
        logger.error(f"Ошибка получения доставок: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/deliveries", tags=["Deliveries"])
def create_delivery(delivery: dict, conn = Depends(get_db)):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO deliveries 
            (shipment_id, recipient_name, recipient_phone, recipient_address, 
             recipient_city, status, signature_required)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING delivery_id
        """, (delivery["shipment_id"], delivery["recipient_name"],
              delivery["recipient_phone"], delivery["recipient_address"],
              delivery["recipient_city"], delivery.get("status", "Ожидает"),
              delivery.get("signature_required", False)))
        
        delivery_id = cur.fetchone()[0]
        conn.commit()
        return {"id": delivery_id, "message": "Доставка успешно создана"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка создания доставки: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/deliveries/{delivery_id}/complete", tags=["Deliveries"])
def complete_delivery(delivery_id: int, conn = Depends(get_db)):
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE deliveries 
            SET status = %s, delivery_time = NOW(), updated_at = NOW()
            WHERE delivery_id = %s
        """, ("Доставлено", delivery_id))
        conn.commit()
        return {"message": "Доставка завершена"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка завершения доставки: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= ANALYTICS =============

@app.get("/api/analytics/revenue", tags=["Analytics"])
def revenue_analytics(conn = Depends(get_db)):
    try:
        cur = conn.cursor()
        
        cur.execute("SELECT COALESCE(SUM(cost), 0) as total FROM orders")
        total_revenue = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM shipments")
        total_shipments = cur.fetchone()[0]
        
        cur.execute("SELECT COALESCE(AVG(cost), 0) as avg FROM shipments WHERE cost > 0")
        avg_cost = cur.fetchone()[0]
        
        return {
            "total_revenue": float(total_revenue),
            "total_shipments": total_shipments,
            "average_shipment_cost": float(avg_cost)
        }
    except Exception as e:
        logger.error(f"Ошибка аналитики: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/driver-performance", tags=["Analytics"])
def driver_performance(conn = Depends(get_db)):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                d.driver_id,
                e.full_name as name,
                COUNT(s.shipment_id) as deliveries,
                COALESCE(d.rating, 5.0) as rating
            FROM drivers d
            JOIN employees e ON d.employee_id = e.employee_id
            LEFT JOIN shipments s ON d.driver_id = s.driver_id 
                AND s.status IN ('В пути', 'Доставлено')
            GROUP BY d.driver_id, e.full_name, d.rating
            ORDER BY deliveries DESC
        """)
        data = cur.fetchall()
        
        return {
            "data": [serialize_row(dict(r)) for r in data]
        }
    except Exception as e:
        logger.error(f"Ошибка производительности: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= ROUTES =============

@app.get("/api/routes", tags=["Routes"])
def get_routes(conn = Depends(get_db)):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT route_id, route_name, start_location, end_location, 
                   distance_km, estimated_duration_hours
            FROM delivery_routes
            WHERE is_active = true
            ORDER BY route_id
        """)
        data = cur.fetchall()
        
        cur.execute("SELECT COUNT(*) FROM delivery_routes WHERE is_active = true")
        total = cur.fetchone()[0]
        
        return {"total": total, "data": [serialize_row(dict(r)) for r in data]}
    except Exception as e:
        logger.error(f"Ошибка получения маршрутов: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= HEALTH CHECK =============

@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
