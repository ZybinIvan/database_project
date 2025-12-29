"""
Упрощенная система управления логистикой и доставкой
FastAPI бэкенд для взаимодействия с БД
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
import logging

DATABASE_URL = "postgresql://logistics:logistics_password@postgres:5432/logistics_db"

app = FastAPI(
    title="Logistics Management System API",
    description="Упрощенное API для управления логистикой",
    version="2.0.0"
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

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class EmployeeModel(Base):
    __tablename__ = "employee"
    employee_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    position = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    hire_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)

class CustomerModel(Base):
    __tablename__ = "customer"
    customer_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

class DriverModel(Base):
    __tablename__ = "driver"
    driver_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee.employee_id"), unique=True, nullable=False)
    license_number = Column(String(20), unique=True, nullable=False)
    experience_years = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)

class VehicleModel(Base):
    __tablename__ = "vehicle"
    vehicle_id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String(20), unique=True, nullable=False)
    vehicle_type = Column(String(50), nullable=False)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    capacity_kg = Column(DECIMAL(10, 2), nullable=False)
    is_available = Column(Boolean, default=True)

class WarehouseModel(Base):
    __tablename__ = "warehouse"
    warehouse_id = Column(Integer, primary_key=True, index=True)
    warehouse_name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    manager_id = Column(Integer, ForeignKey("employee.employee_id"))
    is_active = Column(Boolean, default=True)

class RouteModel(Base):
    __tablename__ = "route"
    route_id = Column(Integer, primary_key=True, index=True)
    route_name = Column(String(255), nullable=False)
    start_location = Column(String(255), nullable=False)
    end_location = Column(String(255), nullable=False)
    distance_km = Column(DECIMAL(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)

class OrderModel(Base):
    __tablename__ = "order_item"
    order_id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouse.warehouse_id"), nullable=False)
    order_date = Column(Date, nullable=False)
    delivery_date = Column(Date, nullable=False)
    status = Column(String(50), default="Pending")
    cost = Column(DECIMAL(10, 2), nullable=False)

class ShipmentModel(Base):
    __tablename__ = "shipment"
    shipment_id = Column(Integer, primary_key=True, index=True)
    shipment_number = Column(String(50), unique=True, nullable=False)
    order_id = Column(Integer, ForeignKey("order_item.order_id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicle.vehicle_id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("driver.driver_id"), nullable=False)
    route_id = Column(Integer, ForeignKey("route.route_id"), nullable=False)
    departure_time = Column(DateTime)
    arrival_time = Column(DateTime)
    status = Column(String(50), default="Pending")
    cost = Column(DECIMAL(10, 2), nullable=False)

class DeliveryModel(Base):
    __tablename__ = "delivery"
    delivery_id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipment.shipment_id"), nullable=False)
    recipient_name = Column(String(255), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    recipient_address = Column(String(255), nullable=False)
    delivery_time = Column(DateTime)
    status = Column(String(50), default="Pending")

class EmployeeSchema(BaseModel):
    full_name: str
    position: str
    phone: str
    hire_date: date
    is_active: bool = True

class CustomerSchema(BaseModel):
    company_name: str
    contact_person: str
    phone: str
    city: str
    address: str
    is_active: bool = True

class DriverSchema(BaseModel):
    employee_id: int
    license_number: str
    experience_years: int
    is_available: bool = True

class VehicleSchema(BaseModel):
    license_plate: str
    vehicle_type: str
    brand: str
    model: str
    capacity_kg: float
    is_available: bool = True

class WarehouseSchema(BaseModel):
    warehouse_name: str
    city: str
    address: str
    manager_id: Optional[int] = None
    is_active: bool = True

class RouteSchema(BaseModel):
    route_name: str
    start_location: str
    end_location: str
    distance_km: float
    is_active: bool = True

class OrderSchema(BaseModel):
    order_number: str
    customer_id: int
    warehouse_id: int
    order_date: date
    delivery_date: date
    status: str = "Pending"
    cost: float

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
    status: str = "Pending"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/employees", tags=["Employees"])
def get_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    employees = db.query(EmployeeModel).offset(skip).limit(limit).all()
    return {"total": db.query(EmployeeModel).count(), "data": employees}

@app.get("/api/employees/{employee_id}", tags=["Employees"])
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(EmployeeModel).filter(EmployeeModel.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.post("/api/employees", tags=["Employees"])
def create_employee(employee: EmployeeSchema, db: Session = Depends(get_db)):
    new_employee = EmployeeModel(**employee.dict())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    logger.info(f"Created employee: {new_employee.full_name}")
    return {"id": new_employee.employee_id, "message": "Employee created"}

@app.put("/api/employees/{employee_id}", tags=["Employees"])
def update_employee(employee_id: int, employee: EmployeeSchema, db: Session = Depends(get_db)):
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
    db_employee = db.query(EmployeeModel).filter(EmployeeModel.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db_employee.is_active = False
    db.commit()
    return {"message": "Employee deactivated"}

@app.get("/api/customers", tags=["Customers"])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = db.query(CustomerModel).offset(skip).limit(limit).all()
    return {"total": db.query(CustomerModel).count(), "data": customers}

@app.post("/api/customers", tags=["Customers"])
def create_customer(customer: CustomerSchema, db: Session = Depends(get_db)):
    new_customer = CustomerModel(**customer.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    logger.info(f"Created customer: {new_customer.company_name}")
    return {"id": new_customer.customer_id, "message": "Customer created"}

@app.get("/api/customers/{customer_id}", tags=["Customers"])
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(CustomerModel).filter(CustomerModel.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.get("/api/drivers", tags=["Drivers"])
def get_drivers(available_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(DriverModel)
    if available_only:
        query = query.filter(DriverModel.is_available == True)
    return {"total": query.count(), "data": query.all()}

@app.post("/api/drivers", tags=["Drivers"])
def create_driver(driver: DriverSchema, db: Session = Depends(get_db)):
    new_driver = DriverModel(**driver.dict())
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    logger.info(f"Created driver with ID: {new_driver.driver_id}")
    return {"id": new_driver.driver_id, "message": "Driver created"}

@app.put("/api/drivers/{driver_id}/availability", tags=["Drivers"])
def update_driver_availability(driver_id: int, is_available: bool, db: Session = Depends(get_db)):
    driver = db.query(DriverModel).filter(DriverModel.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.is_available = is_available
    db.commit()
    return {"message": f"Driver availability set to {is_available}"}

@app.get("/api/vehicles", tags=["Vehicles"])
def get_vehicles(available_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(VehicleModel)
    if available_only:
        query = query.filter(VehicleModel.is_available == True)
    return {"total": query.count(), "data": query.all()}

@app.post("/api/vehicles", tags=["Vehicles"])
def create_vehicle(vehicle: VehicleSchema, db: Session = Depends(get_db)):
    new_vehicle = VehicleModel(**vehicle.dict())
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return {"id": new_vehicle.vehicle_id, "message": "Vehicle created"}

@app.get("/api/warehouses", tags=["Warehouses"])
def get_warehouses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    warehouses = db.query(WarehouseModel).offset(skip).limit(limit).all()
    return {"total": db.query(WarehouseModel).count(), "data": warehouses}

@app.post("/api/warehouses", tags=["Warehouses"])
def create_warehouse(warehouse: WarehouseSchema, db: Session = Depends(get_db)):
    new_warehouse = WarehouseModel(**warehouse.dict())
    db.add(new_warehouse)
    db.commit()
    db.refresh(new_warehouse)
    return {"id": new_warehouse.warehouse_id, "message": "Warehouse created"}

@app.get("/api/routes", tags=["Routes"])
def get_routes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    routes = db.query(RouteModel).filter(RouteModel.is_active == True).offset(skip).limit(limit).all()
    return {"total": db.query(RouteModel).filter(RouteModel.is_active == True).count(), "data": routes}

@app.post("/api/routes", tags=["Routes"])
def create_route(route: RouteSchema, db: Session = Depends(get_db)):
    new_route = RouteModel(**route.dict())
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    logger.info(f"Created route: {new_route.route_name}")
    return {"id": new_route.route_id, "message": "Route created"}

@app.put("/api/routes/{route_id}", tags=["Routes"])
def update_route(route_id: int, route: RouteSchema, db: Session = Depends(get_db)):
    db_route = db.query(RouteModel).filter(RouteModel.route_id == route_id).first()
    if not db_route:
        raise HTTPException(status_code=404, detail="Route not found")
    for key, value in route.dict().items():
        setattr(db_route, key, value)
    db.commit()
    db.refresh(db_route)
    return {"message": "Route updated"}

@app.delete("/api/routes/{route_id}", tags=["Routes"])
def delete_route(route_id: int, db: Session = Depends(get_db)):
    db_route = db.query(RouteModel).filter(RouteModel.route_id == route_id).first()
    if not db_route:
        raise HTTPException(status_code=404, detail="Route not found")
    db_route.is_active = False
    db.commit()
    return {"message": "Route deactivated"}

@app.get("/api/orders", tags=["Orders"])
def get_orders(status: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(OrderModel)
    if status:
        query = query.filter(OrderModel.status == status)
    return {"total": query.count(), "data": query.offset(skip).limit(limit).all()}

@app.post("/api/orders", tags=["Orders"])
def create_order(order: OrderSchema, db: Session = Depends(get_db)):
    new_order = OrderModel(**order.dict())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    logger.info(f"Created order: {new_order.order_number}")
    return {"id": new_order.order_id, "message": "Order created"}

@app.get("/api/orders/{order_id}", tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/api/orders/{order_id}/status", tags=["Orders"])
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    logger.info(f"Order {order_id} status updated to {status}")
    return {"message": "Order status updated"}

@app.get("/api/shipments", tags=["Shipments"])
def get_shipments(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ShipmentModel)
    if status:
        query = query.filter(ShipmentModel.status == status)
    return {"total": query.count(), "data": query.all()}

@app.post("/api/shipments", tags=["Shipments"])
def create_shipment(shipment: ShipmentSchema, db: Session = Depends(get_db)):
    new_shipment = ShipmentModel(**shipment.dict())
    db.add(new_shipment)
    db.commit()
    db.refresh(new_shipment)
    logger.info(f"Created shipment: {new_shipment.shipment_number}")
    return {"id": new_shipment.shipment_id, "message": "Shipment created"}

@app.put("/api/shipments/{shipment_id}/status", tags=["Shipments"])
def update_shipment_status(shipment_id: int, status: str, db: Session = Depends(get_db)):
    shipment = db.query(ShipmentModel).filter(ShipmentModel.shipment_id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    shipment.status = status
    if status == "In Transit":
        shipment.departure_time = datetime.utcnow()
    elif status == "Delivered":
        shipment.arrival_time = datetime.utcnow()
    db.commit()
    return {"message": "Shipment status updated"}

@app.get("/api/deliveries", tags=["Deliveries"])
def get_deliveries(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(DeliveryModel)
    if status:
        query = query.filter(DeliveryModel.status == status)
    return {"total": query.count(), "data": query.all()}

@app.post("/api/deliveries", tags=["Deliveries"])
def create_delivery(delivery: DeliverySchema, db: Session = Depends(get_db)):
    new_delivery = DeliveryModel(**delivery.dict())
    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)
    return {"id": new_delivery.delivery_id, "message": "Delivery created"}

@app.put("/api/deliveries/{delivery_id}/complete", tags=["Deliveries"])
def complete_delivery(delivery_id: int, db: Session = Depends(get_db)):
    delivery = db.query(DeliveryModel).filter(DeliveryModel.delivery_id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    delivery.status = "Delivered"
    delivery.delivery_time = datetime.utcnow()
    db.commit()
    logger.info(f"Delivery {delivery_id} completed")
    return {"message": "Delivery completed"}

@app.get("/api/analytics/dashboard", tags=["Analytics"])
def get_dashboard(db: Session = Depends(get_db)):
    from sqlalchemy import func

    total_orders = db.query(func.count(OrderModel.order_id)).scalar() or 0
    delivered_orders = db.query(func.count(OrderModel.order_id)).filter(
        OrderModel.status == 'Delivered'
    ).scalar() or 0
    in_transit_orders = db.query(func.count(OrderModel.order_id)).filter(
        OrderModel.status == 'In Transit'
    ).scalar() or 0
    available_drivers = db.query(func.count(DriverModel.driver_id)).filter(
        DriverModel.is_available == True
    ).scalar() or 0

    total_revenue = db.query(func.sum(OrderModel.cost)).scalar() or 0
    total_shipments = db.query(func.count(ShipmentModel.shipment_id)).filter(
        ShipmentModel.status == 'Delivered'
    ).scalar() or 0
    avg_shipment_cost = db.query(func.avg(ShipmentModel.cost)).scalar() or 0

    return {
        "total_orders": total_orders,
        "delivered_orders": delivered_orders,
        "in_transit_orders": in_transit_orders,
        "available_drivers": available_drivers,
        "total_revenue": float(total_revenue),
        "total_shipments": total_shipments,
        "avg_shipment_cost": float(avg_shipment_cost)
    }

@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
