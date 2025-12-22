"""
Информационная система управления логистикой и доставкой
FastAPI бэкенд для взаимодействия с БД
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, date, timedelta
from typing import List, Optional
import logging

# ===================================================================
# КОНФИГУРАЦИЯ
# ===================================================================
DATABASE_URL = "postgresql://logistics:logistics_password@postgres:5432/logistics_db"

# Инициализация приложения
app = FastAPI(
    title="Logistics Management System API",
    description="API для управления логистикой и доставкой",
    version="1.0.0"
)

# Добавление CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к БД
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ===================================================================
# ORM МОДЕЛИ (SQLAlchemy)
# ===================================================================

class EmployeeModel(Base):
    __tablename__ = "employees"
    employee_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    position = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    hire_date = Column(Date, nullable=False)
    salary = Column(DECIMAL(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CustomerModel(Base):
    __tablename__ = "customers"
    customer_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    postal_code = Column(String(10))
    registration_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DriverModel(Base):
    __tablename__ = "drivers"
    driver_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), unique=True, nullable=False)
    license_number = Column(String(20), unique=True, nullable=False)
    license_expiry_date = Column(Date, nullable=False)
    experience_years = Column(Integer, nullable=False)
    rating = Column(DECIMAL(3, 2), default=5.00)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class VehicleModel(Base):
    __tablename__ = "vehicles"
    vehicle_id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String(20), unique=True, nullable=False)
    vehicle_type = Column(String(50), nullable=False)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    capacity_kg = Column(DECIMAL(10, 2), nullable=False)
    capacity_cubic_m = Column(DECIMAL(10, 2), nullable=False)
    mileage = Column(Integer, default=0)
    last_maintenance = Column(Date)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class WarehouseModel(Base):
    __tablename__ = "warehouses"
    warehouse_id = Column(Integer, primary_key=True, index=True)
    warehouse_name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    postal_code = Column(String(10))
    manager_id = Column(Integer, ForeignKey("employees.employee_id"))
    capacity_items = Column(Integer, nullable=False)
    current_items = Column(Integer, default=0)
    phone = Column(String(20))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class RouteModel(Base):
    __tablename__ = "delivery_routes"
    route_id = Column(Integer, primary_key=True, index=True)
    route_name = Column(String(255), nullable=False)
    start_location = Column(String(255), nullable=False)
    end_location = Column(String(255), nullable=False)
    distance_km = Column(DECIMAL(10, 2), nullable=False)
    estimated_duration_hours = Column(DECIMAL(5, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class OrderModel(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id"), nullable=False)
    order_date = Column(Date, nullable=False)
    delivery_date = Column(Date, nullable=False)
    description = Column(String(500))
    total_weight_kg = Column(DECIMAL(10, 2))
    total_volume_cubic_m = Column(DECIMAL(10, 2))
    status = Column(String(50), default="Pending")
    priority = Column(String(20), default="Normal")
    cost = Column(DECIMAL(10, 2), nullable=False)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ShipmentModel(Base):
    __tablename__ = "shipments"
    shipment_id = Column(Integer, primary_key=True, index=True)
    shipment_number = Column(String(50), unique=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.vehicle_id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"), nullable=False)
    route_id = Column(Integer, ForeignKey("delivery_routes.route_id"), nullable=False)
    departure_time = Column(DateTime)
    expected_arrival_time = Column(DateTime)
    actual_arrival_time = Column(DateTime)
    status = Column(String(50), default="Pending")
    distance_traveled_km = Column(DECIMAL(10, 2))
    fuel_consumed_liters = Column(DECIMAL(10, 2))
    cost = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DeliveryModel(Base):
    __tablename__ = "deliveries"
    delivery_id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.shipment_id"), nullable=False)
    recipient_name = Column(String(255), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    recipient_address = Column(String(255), nullable=False)
    recipient_city = Column(String(100), nullable=False)
    delivery_time = Column(DateTime)
    signature_required = Column(Boolean, default=False)
    signature_obtained = Column(Boolean, default=False)
    signature_date = Column(DateTime)
    delivery_notes = Column(String)
    status = Column(String(50), default="Pending")
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ===================================================================
# PYDANTIC СХЕМЫ (для валидации API запросов)
# ===================================================================

class EmployeeSchema(BaseModel):
    full_name: str
    position: str
    email: str
    phone: str
    hire_date: date
    salary: float
    is_active: bool = True

class CustomerSchema(BaseModel):
    company_name: str
    contact_person: str
    email: Optional[str] = None
    phone: str
    city: str
    address: str
    postal_code: Optional[str] = None
    registration_date: date
    is_active: bool = True

class DriverSchema(BaseModel):
    employee_id: int
    license_number: str
    license_expiry_date: date
    experience_years: int
    rating: float = 5.00
    is_available: bool = True

class VehicleSchema(BaseModel):
    license_plate: str
    vehicle_type: str
    brand: str
    model: str
    year: int
    capacity_kg: float
    capacity_cubic_m: float
    is_available: bool = True

class OrderSchema(BaseModel):
    order_number: str
    customer_id: int
    warehouse_id: int
    order_date: date
    delivery_date: date
    description: Optional[str] = None
    total_weight_kg: Optional[float] = None
    total_volume_cubic_m: Optional[float] = None
    status: str = "Pending"
    priority: str = "Normal"
    cost: float
    notes: Optional[str] = None

class ShipmentSchema(BaseModel):
    shipment_number: str
    order_id: int
    vehicle_id: int
    driver_id: int
    route_id: int
    status: str = "Pending"
    cost: float

class DeliverySchema(BaseModel):
    shipment_id: int
    recipient_name: str
    recipient_phone: str
    recipient_address: str
    recipient_city: str
    signature_required: bool = False
    status: str = "Pending"

# Получение сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===================================================================
# ЭНДПОИНТЫ: СОТРУДНИКИ
# ===================================================================

@app.get("/api/employees", tags=["Employees"])
def get_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список всех сотрудников"""
    employees = db.query(EmployeeModel).offset(skip).limit(limit).all()
    return {"total": db.query(EmployeeModel).count(), "data": employees}

@app.get("/api/employees/{employee_id}", tags=["Employees"])
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """Получить информацию о конкретном сотруднике"""
    employee = db.query(EmployeeModel).filter(EmployeeModel.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.post("/api/employees", tags=["Employees"])
def create_employee(employee: EmployeeSchema, db: Session = Depends(get_db)):
    """Создать нового сотрудника"""
    new_employee = EmployeeModel(**employee.dict())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    logger.info(f"Created employee: {new_employee.full_name}")
    return {"id": new_employee.employee_id, "message": "Employee created"}

@app.put("/api/employees/{employee_id}", tags=["Employees"])
def update_employee(employee_id: int, employee: EmployeeSchema, db: Session = Depends(get_db)):
    """Обновить информацию сотрудника"""
    db_employee = db.query(EmployeeModel).filter(EmployeeModel.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    for key, value in employee.dict().items():
        setattr(db_employee, key, value)
    db.commit()
    db.refresh(db_employee)
    return {"message": "Employee updated"}

@app.delete("/api/employees/{employee_id}", tags=["Employees"])
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """Удалить сотрудника (мягкое удаление)"""
    db_employee = db.query(EmployeeModel).filter(EmployeeModel.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db_employee.is_active = False
    db.commit()
    return {"message": "Employee deactivated"}

# ===================================================================
# ЭНДПОИНТЫ: КЛИЕНТЫ
# ===================================================================

@app.get("/api/customers", tags=["Customers"])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список всех клиентов"""
    customers = db.query(CustomerModel).offset(skip).limit(limit).all()
    return {"total": db.query(CustomerModel).count(), "data": customers}

@app.post("/api/customers", tags=["Customers"])
def create_customer(customer: CustomerSchema, db: Session = Depends(get_db)):
    """Создать нового клиента"""
    new_customer = CustomerModel(**customer.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    logger.info(f"Created customer: {new_customer.company_name}")
    return {"id": new_customer.customer_id, "message": "Customer created"}

@app.get("/api/customers/{customer_id}", tags=["Customers"])
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Получить информацию о клиенте"""
    customer = db.query(CustomerModel).filter(CustomerModel.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# ===================================================================
# ЭНДПОИНТЫ: ВОДИТЕЛИ
# ===================================================================

@app.get("/api/drivers", tags=["Drivers"])
def get_drivers(available_only: bool = False, db: Session = Depends(get_db)):
    """Получить список водителей"""
    query = db.query(DriverModel)
    if available_only:
        query = query.filter(DriverModel.is_available == True)
    return {"total": query.count(), "data": query.all()}

@app.post("/api/drivers", tags=["Drivers"])
def create_driver(driver: DriverSchema, db: Session = Depends(get_db)):
    """Создать нового водителя"""
    new_driver = DriverModel(**driver.dict())
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    logger.info(f"Created driver with ID: {new_driver.driver_id}")
    return {"id": new_driver.driver_id, "message": "Driver created"}

@app.put("/api/drivers/{driver_id}/availability", tags=["Drivers"])
def update_driver_availability(driver_id: int, is_available: bool, db: Session = Depends(get_db)):
    """Изменить статус доступности водителя"""
    driver = db.query(DriverModel).filter(DriverModel.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.is_available = is_available
    db.commit()
    return {"message": f"Driver availability set to {is_available}"}

# ===================================================================
# ЭНДПОИНТЫ: ТРАНСПОРТНЫЕ СРЕДСТВА
# ===================================================================

@app.get("/api/vehicles", tags=["Vehicles"])
def get_vehicles(available_only: bool = False, db: Session = Depends(get_db)):
    """Получить список транспортных средств"""
    query = db.query(VehicleModel)
    if available_only:
        query = query.filter(VehicleModel.is_available == True)
    return {"total": query.count(), "data": query.all()}

@app.post("/api/vehicles", tags=["Vehicles"])
def create_vehicle(vehicle: VehicleSchema, db: Session = Depends(get_db)):
    """Добавить новое транспортное средство"""
    new_vehicle = VehicleModel(**vehicle.dict())
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return {"id": new_vehicle.vehicle_id, "message": "Vehicle created"}

# ===================================================================
# ЭНДПОИНТЫ: ЗАКАЗЫ
# ===================================================================

@app.get("/api/orders", tags=["Orders"])
def get_orders(status: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список заказов с фильтрацией по статусу"""
    query = db.query(OrderModel)
    if status:
        query = query.filter(OrderModel.status == status)
    return {
        "total": query.count(),
        "data": query.offset(skip).limit(limit).all()
    }

@app.post("/api/orders", tags=["Orders"])
def create_order(order: OrderSchema, db: Session = Depends(get_db)):
    """Создать новый заказ"""
    new_order = OrderModel(**order.dict())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    logger.info(f"Created order: {new_order.order_number}")
    return {"id": new_order.order_id, "message": "Order created"}

@app.get("/api/orders/{order_id}", tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Получить информацию о заказе"""
    order = db.query(OrderModel).filter(OrderModel.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/api/orders/{order_id}/status", tags=["Orders"])
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    """Изменить статус заказа"""
    order = db.query(OrderModel).filter(OrderModel.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    order.updated_at = datetime.utcnow()
    db.commit()
    logger.info(f"Order {order_id} status updated to {status}")
    return {"message": "Order status updated"}

# ===================================================================
# ЭНДПОИНТЫ: ПАРТИИ ДОСТАВКИ (SHIPMENTS)
# ===================================================================

@app.get("/api/shipments", tags=["Shipments"])
def get_shipments(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Получить список партий доставки"""
    query = db.query(ShipmentModel)
    if status:
        query = query.filter(ShipmentModel.status == status)
    return {"total": query.count(), "data": query.all()}

@app.post("/api/shipments", tags=["Shipments"])
def create_shipment(shipment: ShipmentSchema, db: Session = Depends(get_db)):
    """Создать новую партию доставки"""
    new_shipment = ShipmentModel(**shipment.dict())
    db.add(new_shipment)
    db.commit()
    db.refresh(new_shipment)
    logger.info(f"Created shipment: {new_shipment.shipment_number}")
    return {"id": new_shipment.shipment_id, "message": "Shipment created"}

@app.put("/api/shipments/{shipment_id}/status", tags=["Shipments"])
def update_shipment_status(shipment_id: int, status: str, db: Session = Depends(get_db)):
    """Изменить статус доставки"""
    shipment = db.query(ShipmentModel).filter(ShipmentModel.shipment_id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    shipment.status = status
    if status == "In Transit":
        shipment.departure_time = datetime.utcnow()
    elif status == "Delivered":
        shipment.actual_arrival_time = datetime.utcnow()
    shipment.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Shipment status updated"}

# ===================================================================
# ЭНДПОИНТЫ: ДОСТАВКИ
# ===================================================================

@app.get("/api/deliveries", tags=["Deliveries"])
def get_deliveries(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Получить список доставок"""
    query = db.query(DeliveryModel)
    if status:
        query = query.filter(DeliveryModel.status == status)
    return {"total": query.count(), "data": query.all()}

@app.post("/api/deliveries", tags=["Deliveries"])
def create_delivery(delivery: DeliverySchema, db: Session = Depends(get_db)):
    """Создать новую доставку"""
    new_delivery = DeliveryModel(**delivery.dict())
    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)
    return {"id": new_delivery.delivery_id, "message": "Delivery created"}

@app.put("/api/deliveries/{delivery_id}/complete", tags=["Deliveries"])
def complete_delivery(delivery_id: int, db: Session = Depends(get_db)):
    """Отметить доставку как выполненную"""
    delivery = db.query(DeliveryModel).filter(DeliveryModel.delivery_id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    delivery.status = "Delivered"
    delivery.delivery_time = datetime.utcnow()
    delivery.updated_at = datetime.utcnow()
    db.commit()
    logger.info(f"Delivery {delivery_id} completed")
    return {"message": "Delivery completed"}

# ===================================================================
# АНАЛИТИЧЕСКИЕ ЭНДПОИНТЫ
# ===================================================================

@app.get("/api/analytics/orders-by-status", tags=["Analytics"])
def orders_by_status(db: Session = Depends(get_db)):
    """Статистика заказов по статусам"""
    from sqlalchemy import func
    result = db.query(
        OrderModel.status,
        func.count(OrderModel.order_id).label("count")
    ).group_by(OrderModel.status).all()
    return {"data": [{"status": r[0], "count": r[1]} for r in result]}

@app.get("/api/analytics/revenue", tags=["Analytics"])
def revenue_analytics(db: Session = Depends(get_db)):
    """Аналитика доходов"""
    from sqlalchemy import func
    total_revenue = db.query(func.sum(OrderModel.cost)).scalar() or 0
    total_shipments = db.query(func.count(ShipmentModel.shipment_id)).scalar() or 0
    avg_shipment_cost = db.query(func.avg(ShipmentModel.cost)).scalar() or 0
    
    return {
        "total_revenue": float(total_revenue),
        "total_shipments": total_shipments,
        "average_shipment_cost": float(avg_shipment_cost)
    }

@app.get("/api/analytics/driver-performance", tags=["Analytics"])
def driver_performance(db: Session = Depends(get_db)):
    """Производительность водителей"""
    from sqlalchemy import func
    result = db.query(
        DriverModel.driver_id,
        EmployeeModel.full_name,
        func.count(ShipmentModel.shipment_id).label("deliveries"),
        DriverModel.rating
    ).join(EmployeeModel).outerjoin(ShipmentModel).group_by(
        DriverModel.driver_id, EmployeeModel.full_name, DriverModel.rating
    ).all()
    
    return {
        "data": [
            {
                "driver_id": r[0],
                "name": r[1],
                "deliveries": r[2],
                "rating": float(r[3])
            }
            for r in result
        ]
    }

# ===================================================================
# HEALTH CHECK
# ===================================================================

@app.get("/api/health", tags=["System"])
def health_check():
    """Проверка статуса API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
