from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://logistics:logistics_password@postgres:5432/logistics_db')

app = FastAPI(title='Logistics Management System API', description='API for Logistics', version='1.0.0')

app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f'DB Connection Error: {e}')
        raise

def format_date(dateobj):
    if dateobj is None:
        return None
    if isinstance(dateobj, str):
        return dateobj
    if isinstance(dateobj, (datetime, date)):
        return dateobj.strftime('%d.%m.%Y')
    return str(dateobj)

def format_datetime(dtobj):
    if dtobj is None:
        return None
    if isinstance(dtobj, str):
        return dtobj
    if isinstance(dtobj, datetime):
        return dtobj.strftime('%d.%m.%Y %H:%M')
    return str(dtobj)

def serialize_row(row):
    if row is None:
        return None
    result = {}
    for key, value in dict(row).items():
        try:
            if value is None:
                result[key] = None
            elif isinstance(value, bool):
                result[key] = value
            elif isinstance(value, (int, float)):
                result[key] = value
            elif isinstance(value, (datetime, date)):
                if 'date' in key.lower() or 'created' in key.lower() or 'updated' in key.lower():
                    result[key] = format_date(value)
                else:
                    result[key] = format_datetime(value)
            else:
                result[key] = str(value)
        except Exception as e:
            result[key] = str(value) if value is not None else None
    return result

def serialize_rows(rows):
    if not rows:
        return []
    return [serialize_row(row) for row in rows]

class OrderCreate(BaseModel):
    customer_id: int
    warehouse_id: int
    order_date: date
    delivery_date: date
    status: str = 'Ожидает'
    priority: str
    cost: float
    description: Optional[str] = None

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    cost: Optional[float] = None
    delivery_date: Optional[date] = None

class ShipmentCreate(BaseModel):
    order_id: int
    vehicle_id: int
    driver_id: int
    route_id: int
    status: str = 'Ожидает'
    cost: float

class ShipmentStatusUpdate(BaseModel):
    status: str

class CustomerCreate(BaseModel):
    company_name: str
    contact_person: str
    phone: str
    city: str
    address: str
    email: Optional[str] = None
    postal_code: Optional[str] = None

class DriverCreate(BaseModel):
    employee_id: int
    license_number: str
    license_expiry_date: date
    experience_years: int

class VehicleCreate(BaseModel):
    license_plate: str
    vehicle_type: str
    brand: str
    model: str
    year: int
    capacity_kg: float
    capacity_cubic_m: float

class EmployeeCreate(BaseModel):
    fullname: str
    position: str
    email: str
    phone: str
    hire_date: date
    salary: float

@app.get('/api/health', tags=['System'])
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}

@app.get('/api/orders', tags=['Orders'])
def get_orders(status: Optional[str] = None, skip: int = 0, limit: int = 100):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = 'SELECT o.order_id as id, o.customer_id, c.contact_person as customer_name, c.company_name, o.status, o.priority, o.cost, o.order_date, o.delivery_date, o.description FROM orders o JOIN customers c ON o.customer_id = c.customer_id'
        params = []
        if status:
            query += ' WHERE o.status = %s'
            params.append(status)
        query += ' ORDER BY o.order_id DESC LIMIT %s OFFSET %s'
        params.extend([limit, skip])
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.execute('SELECT COUNT(*) FROM orders')
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {'total': total, 'data': serialize_rows(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/orders/{order_id}', tags=['Orders'])
def get_order(order_id: int):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT o.*, c.contact_person as customer_name, c.company_name FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_id = %s', (order_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail='Order not found')
        return serialize_row(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/orders', tags=['Orders'])
def create_order(order: OrderCreate):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('INSERT INTO orders (customer_id, warehouse_id, order_date, delivery_date, status, priority, cost, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING order_id', (order.customer_id, order.warehouse_id, order.order_date, order.delivery_date, order.status, order.priority, order.cost, order.description))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return {'id': result['order_id'], 'message': 'Order created'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put('/api/orders/{order_id}', tags=['Orders'])
def update_order(order_id: int, order: OrderUpdate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        updates = []
        params = []
        if order.status:
            updates.append('status = %s')
            params.append(order.status)
        if order.priority:
            updates.append('priority = %s')
            params.append(order.priority)
        if order.cost:
            updates.append('cost = %s')
            params.append(order.cost)
        if order.delivery_date:
            updates.append('delivery_date = %s')
            params.append(order.delivery_date)
        if not updates:
            raise HTTPException(status_code=400, detail='No fields to update')
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(order_id)
        query = f"UPDATE orders SET {', '.join(updates)} WHERE order_id = %s"
        cur.execute(query, params)
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail='Order not found')
        cur.close()
        conn.close()
        return {'message': 'Order updated'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/shipments', tags=['Shipments'])
def get_shipments(status: Optional[str] = None):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = 'SELECT s.shipment_id as id, s.order_id, o.customer_id, c.contact_person as customer_name, v.license_plate, v.brand, v.model, e.fullname as driver_name, s.status, s.cost, s.created_at FROM shipments s JOIN orders o ON s.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id JOIN vehicles v ON s.vehicle_id = v.vehicle_id JOIN drivers d ON s.driver_id = d.driver_id JOIN employees e ON d.employee_id = e.employee_id'
        if status:
            query += ' WHERE s.status = %s'
            cur.execute(query, (status,))
        else:
            cur.execute(query)
        rows = cur.fetchall()
        cur.execute('SELECT COUNT(*) FROM shipments')
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {'total': total, 'data': serialize_rows(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/shipments', tags=['Shipments'])
def create_shipment(shipment: ShipmentCreate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO shipments (order_id, vehicle_id, driver_id, route_id, status, cost) VALUES (%s, %s, %s, %s, %s, %s) RETURNING shipment_id', (shipment.order_id, shipment.vehicle_id, shipment.driver_id, shipment.route_id, shipment.status, shipment.cost))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return {'id': result[0], 'message': 'Shipment created'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put('/api/shipments/{shipment_id}/status', tags=['Shipments'])
def update_shipment_status(shipment_id: int, update: ShipmentStatusUpdate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE shipments SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE shipment_id = %s', (update.status, shipment_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail='Shipment not found')
        cur.close()
        conn.close()
        return {'message': 'Shipment status updated'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/customers', tags=['Customers'])
def get_customers(skip: int = 0, limit: int = 100):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM customers ORDER BY customer_id DESC LIMIT %s OFFSET %s', (limit, skip))
        rows = cur.fetchall()
        cur.execute('SELECT COUNT(*) FROM customers')
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {'total': total, 'data': serialize_rows(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/customers', tags=['Customers'])
def create_customer(customer: CustomerCreate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO customers (company_name, contact_person, email, phone, city, address, postal_code) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING customer_id', (customer.company_name, customer.contact_person, customer.email, customer.phone, customer.city, customer.address, customer.postal_code))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return {'id': result[0], 'message': 'Customer created'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/drivers', tags=['Drivers'])
def get_drivers(available_only: bool = False):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = 'SELECT d.driver_id as id, d.employee_id, e.fullname, d.license_number, d.license_expiry_date, d.experience_years, d.rating, d.is_available FROM drivers d JOIN employees e ON d.employee_id = e.employee_id'
        if available_only:
            query += ' WHERE d.is_available = TRUE'
        query += ' ORDER BY d.driver_id'
        cur.execute(query)
        rows = cur.fetchall()
        cur.execute('SELECT COUNT(*) FROM drivers')
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {'total': total, 'data': serialize_rows(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/drivers', tags=['Drivers'])
def create_driver(driver: DriverCreate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO drivers (employee_id, license_number, license_expiry_date, experience_years) VALUES (%s, %s, %s, %s) RETURNING driver_id', (driver.employee_id, driver.license_number, driver.license_expiry_date, driver.experience_years))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return {'id': result[0], 'message': 'Driver created'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/vehicles', tags=['Vehicles'])
def get_vehicles():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM vehicles ORDER BY vehicle_id')
        rows = cur.fetchall()
        cur.execute('SELECT COUNT(*) FROM vehicles')
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {'total': total, 'data': serialize_rows(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/vehicles', tags=['Vehicles'])
def create_vehicle(vehicle: VehicleCreate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO vehicles (license_plate, vehicle_type, brand, model, year, capacity_kg, capacity_cubic_m) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING vehicle_id', (vehicle.license_plate, vehicle.vehicle_type, vehicle.brand, vehicle.model, vehicle.year, vehicle.capacity_kg, vehicle.capacity_cubic_m))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return {'id': result[0], 'message': 'Vehicle created'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/employees', tags=['Employees'])
def get_employees():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM employees WHERE is_active = TRUE ORDER BY employee_id')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'total': len(rows), 'data': serialize_rows(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/employees', tags=['Employees'])
def create_employee(employee: EmployeeCreate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO employees (fullname, position, email, phone, hire_date, salary) VALUES (%s, %s, %s, %s, %s, %s) RETURNING employee_id', (employee.fullname, employee.position, employee.email, employee.phone, employee.hire_date, employee.salary))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return {'id': result[0], 'message': 'Employee created'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/warehouses', tags=['Warehouses'])
def get_warehouses():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM warehouses WHERE is_active = TRUE ORDER BY warehouse_id')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'total': len(rows), 'data': serialize_rows(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/routes', tags=['Routes'])
def get_routes():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM delivery_routes WHERE is_active = TRUE ORDER BY route_id')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'total': len(rows), 'data': serialize_rows(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/analytics/revenue', tags=['Analytics'])
def revenue_analytics():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT COALESCE(SUM(cost), 0) as total_revenue, COUNT(*) as total_orders, COUNT(CASE WHEN status = \'Доставлено\' THEN 1 END) as delivered_orders, ROUND(AVG(cost)::NUMERIC, 2) as avg_order_cost FROM orders')
        result = cur.fetchone()
        cur.close()
        conn.close()
        return serialize_row(result) if result else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/analytics/driver-performance', tags=['Analytics'])
def driver_performance():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT d.driver_id as id, e.fullname, COUNT(s.shipment_id) as deliveries, COALESCE(AVG(d.rating), 5.0) as rating FROM drivers d JOIN employees e ON d.employee_id = e.employee_id LEFT JOIN shipments s ON d.driver_id = s.driver_id GROUP BY d.driver_id, e.fullname ORDER BY rating DESC')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'data': serialize_rows(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/deliveries', tags=['Deliveries'])
def get_deliveries():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM deliveries ORDER BY delivery_id DESC LIMIT 100')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'total': len(rows), 'data': serialize_rows(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
