# 🚚 Система управления логистикой и доставкой

**Полная документация проекта с описанием БД, Backend и Frontend**

---

## 📋 Содержание

1. [Обзор проекта](#обзор-проекта)
2. [Архитектура системы](#архитектура-системы)
3. [Структура базы данных](#структура-базы-данных)
4. [Backend API (FastAPI)](#backend-api-fastapi)
5. [Frontend (HTML/JavaScript)](#frontend-htmljavascript)
6. [Установка и запуск](#установка-и-запуск)
7. [Использование API](#использование-api)
8. [Примеры запросов](#примеры-запросов)

---

## 🎯 Обзор проекта

**Информационная система управления логистикой и доставкой** - это полнофункциональное веб-приложение для управления грузоперевозками, заказами, доставками и аналитикой в режиме реального времени.

### Основные возможности:

- ✅ Управление сотрудниками и водителями
- ✅ Ведение каталога клиентов и поставщиков
- ✅ Контроль транспортных средств и их обслуживания
- ✅ Управление складами и товарами
- ✅ Создание и отслеживание заказов
- ✅ Управление партиями доставки (shipments)
- ✅ Отслеживание доставок на дом
- ✅ Аналитика и отчеты по производительности
- ✅ REST API для интеграции с другими системами

### Технологический стек:

```
Backend:  FastAPI + SQLAlchemy + PostgreSQL
Frontend: HTML5 + CSS3 + JavaScript (Vanilla)
Database: PostgreSQL 15+
Docker:   Docker + Docker Compose
Deployment: Linux/Windows/macOS
```

---

## 🏗️ Архитектура системы

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                           │
│          (HTML5 + JavaScript Frontend)                   │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP/REST
                  ↓
┌─────────────────────────────────────────────────────────┐
│                 Nginx Web Server                         │
│         (Reverse Proxy + Static Files)                   │
│                Port 8001                                 │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP
                  ↓
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend Server                      │
│          (API Routes + Business Logic)                   │
│                Port 8000                                 │
└─────────────────┬───────────────────────────────────────┘
                  │ TCP/IP
                  ↓
┌─────────────────────────────────────────────────────────┐
│          PostgreSQL Database Server                      │
│         (Data Storage + Relationships)                   │
│                Port 5432                                 │
└─────────────────────────────────────────────────────────┘

Docker Compose Network (All containers connected)
```

---

## 📊 Структура базы данных

### Диаграмма сущностей (ER)

```
employees (1) ──→ (N) drivers
    ↑                  ↓
    │                  (1)
    │                   ↑
    │              (N) shipments → (1) orders
    │                   ↓              ↓
    │              (1) vehicles   (1) warehouses
    │                   ↑              ↑
    └───────────────────┴──────────────┘
                        (N) customers
    
Additional:
deliveries ← shipments
routes ← shipments
```

### Подробное описание таблиц

#### 1️⃣ **employees** (Сотрудники)

```sql
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    position VARCHAR(100) NOT NULL,      -- Должность
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    hire_date DATE NOT NULL,              -- Дата приема
    salary DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Назначение:** Хранение информации о сотрудниках компании (директоры, менеджеры, логисты)

**Пример данных:**
```
| ID | Имя              | Должность           | Email                      | Зарплата |
|----|------------------|---------------------|----------------------------|----------|
| 1  | Иван Петров      | Директор            | ivan.petrov@logistics.ru   | 75000    |
| 2  | Мария Сидорова   | Менеджер            | maria.sidorova@logistics.ru| 65000    |
| 3  | Сергей Кузнецов  | Водитель            | sergey.kuznetsov@...       | 55000    |
```

---

#### 2️⃣ **customers** (Клиенты)

```sql
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
```

**Назначение:** Реестр клиентов (компаний), заказывающих доставку

**Пример:**
```
| ID | Компания                    | Контакт              | Город             |
|----|-----------------------------|--------------------|-------------------|
| 1  | ООО "Альфа Экспресс"       | Петр Иванов        | Москва            |
| 2  | ИП "Бета Логистика"        | Виктория Петрова   | Санкт-Петербург   |
```

---

#### 3️⃣ **drivers** (Водители)

```sql
CREATE TABLE drivers (
    driver_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL UNIQUE,      -- Связь с сотрудником
    license_number VARCHAR(20) UNIQUE NOT NULL,
    license_expiry_date DATE NOT NULL,    -- Срок действия прав
    experience_years INT NOT NULL,        -- Опыт вождения
    rating DECIMAL(3, 2) DEFAULT 5.00,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);
```

**Назначение:** Дополнительная информация о водителях с лицензиями

**Связь:** Водитель → Сотрудник (1:1)

---

#### 4️⃣ **vehicles** (Транспортные средства)

```sql
CREATE TABLE vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    license_plate VARCHAR(20) UNIQUE NOT NULL,  -- Гос. номер
    vehicle_type VARCHAR(50) NOT NULL,          -- Car, Van, Truck
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    capacity_kg DECIMAL(10, 2) NOT NULL,        -- Вес, кг
    capacity_cubic_m DECIMAL(10, 2) NOT NULL,   -- Объем, м³
    mileage INT DEFAULT 0,                      -- Пробег
    last_maintenance DATE,                      -- Последнее ТО
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Назначение:** Реестр автотранспорта компании

**Примеры:**
```
| Номер    | Тип   | Марка    | Объем | Вес     | Статус       |
|----------|-------|----------|-------|---------|--------------|
| МТ123АА  | Car   | Toyota   | 0.5м³ | 200кг   | Доступен     |
| МТ300СС  | Truck | Volvo    | 65м³  | 15000кг | На обслужив. |
```

---

#### 5️⃣ **warehouses** (Склады)

```sql
CREATE TABLE warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    warehouse_name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    postal_code VARCHAR(10),
    manager_id INT,                       -- Менеджер склада
    capacity_items INT NOT NULL,          -- Макс. кол-во товаров
    current_items INT DEFAULT 0,          -- Текущее кол-во
    phone VARCHAR(20),
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);
```

**Назначение:** Управление складами и запасами

**Пример:**
```
| ID | Название           | Город          | Вместимость | Текущие товары |
|----|-------------------|----------------|-------------|----------------|
| 1  | Московский склад   | Москва         | 10000       | 7500           |
| 2  | Центральный хаб    | Екатеринбург   | 15000       | 12000          |
```

---

#### 6️⃣ **delivery_routes** (Маршруты доставки)

```sql
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
```

**Назначение:** Основные маршруты между городами

**Примеры:**
```
| ID | Маршрут                    | Расстояние | Время |
|----|----------------------------|-----------|-------|
| 1  | Москва - Санкт-Петербург   | 700 км    | 10ч   |
| 2  | Москва - Екатеринбург      | 1800 км   | 24ч   |
```

---

#### 7️⃣ **orders** (Заказы)

```sql
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,  -- ORD-2024-00001
    customer_id INT NOT NULL,                  -- Клиент
    warehouse_id INT NOT NULL,                 -- Исходной склад
    order_date DATE NOT NULL,
    delivery_date DATE NOT NULL,               -- Планируемая дата
    description VARCHAR(500),
    total_weight_kg DECIMAL(10, 2),
    total_volume_cubic_m DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'Pending',      -- Статус заказа
    priority VARCHAR(20) DEFAULT 'Normal',     -- Low, Normal, High, Urgent
    cost DECIMAL(10, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
);
```

**Назначение:** Реестр заказов на доставку

**Статусы:** Pending → Processing → Shipped → Delivered → Cancelled

**Пример:**
```
| Номер         | Клиент ID | Статус    | Приоритет | Стоимость |
|---------------|-----------|-----------|-----------|-----------|
| ORD-2024-00001| 1         | Delivered | Normal    | 35000     |
| ORD-2024-00002| 2         | In Transit| High      | 52000     |
```

---

#### 8️⃣ **shipments** (Партии доставки)

```sql
CREATE TABLE shipments (
    shipment_id SERIAL PRIMARY KEY,
    shipment_number VARCHAR(50) UNIQUE NOT NULL,  -- SHIP-2024-00001
    order_id INT NOT NULL,                        -- Заказ
    vehicle_id INT NOT NULL,                      -- Транспорт
    driver_id INT NOT NULL,                       -- Водитель
    route_id INT NOT NULL,                        -- Маршрут
    departure_time TIMESTAMP,
    expected_arrival_time TIMESTAMP,
    actual_arrival_time TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Pending',         -- Статус доставки
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
```

**Назначение:** Конкретная партия (отправка) с указанием машины и водителя

**Статусы:** Pending → In Transit → Delivered → Delayed → Failed

---

#### 9️⃣ **deliveries** (Доставки)

```sql
CREATE TABLE deliveries (
    delivery_id SERIAL PRIMARY KEY,
    shipment_id INT NOT NULL,              -- Партия доставки
    recipient_name VARCHAR(255) NOT NULL,  -- Получатель
    recipient_phone VARCHAR(20) NOT NULL,
    recipient_address VARCHAR(255) NOT NULL,
    recipient_city VARCHAR(100) NOT NULL,
    delivery_time TIMESTAMP,
    signature_required BOOLEAN DEFAULT FALSE,
    signature_obtained BOOLEAN DEFAULT FALSE,
    signature_date TIMESTAMP,
    delivery_notes TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    attempts INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
);
```

**Назначение:** Финальная доставка адресату

**Статусы:** Pending → In Transit → Delivered → Failed → Reattempt

---

### Индексы и оптимизация

```sql
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_delivery_date ON orders(delivery_date);
CREATE INDEX idx_shipments_vehicle ON shipments(vehicle_id);
CREATE INDEX idx_shipments_driver ON shipments(driver_id);
CREATE INDEX idx_shipments_status ON shipments(status);
CREATE INDEX idx_deliveries_shipment ON deliveries(shipment_id);
CREATE INDEX idx_deliveries_status ON deliveries(status);
```

---

### Представления (Views)

#### View: order_statistics
```sql
CREATE VIEW order_statistics AS
SELECT 
    COUNT(*) as total_orders,
    COUNT(CASE WHEN status = 'Delivered' THEN 1 END) as delivered_orders,
    COUNT(CASE WHEN status = 'In Transit' THEN 1 END) as in_transit_orders,
    ROUND(AVG(cost)::NUMERIC, 2) as avg_order_cost,
    SUM(cost) as total_revenue
FROM orders;
```

#### View: driver_activity
```sql
CREATE VIEW driver_activity AS
SELECT 
    d.driver_id,
    e.full_name,
    COUNT(s.shipment_id) as total_shipments,
    AVG(d.rating) as avg_rating,
    COUNT(CASE WHEN s.status = 'Delivered' THEN 1 END) as delivered_shipments
FROM drivers d
JOIN employees e ON d.employee_id = e.employee_id
LEFT JOIN shipments s ON d.driver_id = s.driver_id
GROUP BY d.driver_id, e.full_name;
```

---

## 🔌 Backend API (FastAPI)

### Установка зависимостей

```bash
pip install fastapi sqlalchemy psycopg2-binary uvicorn pydantic python-dotenv
```

### Структура кода

```python
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, date

# === КОНФИГУРАЦИЯ ===
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://logistics:logistics_password@postgres:5432/logistics_db"
)

app = FastAPI(
    title="Logistics Management System API",
    description="API для управления логистикой и доставкой",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# БД
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### Модели данных (SQLAlchemy ORM)

#### Employee Model
```python
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
```

#### Order Model
```python
class OrderModel(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id"), nullable=False)
    order_date = Column(Date, nullable=False)
    delivery_date = Column(Date, nullable=False)
    total_weight_kg = Column(DECIMAL(10, 2))
    total_volume_cubic_m = Column(DECIMAL(10, 2))
    status = Column(String(50), default="Pending")  # Pending, Processing, Shipped, Delivered
    priority = Column(String(20), default="Normal")  # Low, Normal, High, Urgent
    cost = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

### Pydantic Schemas (Валидация)

```python
class OrderSchema(BaseModel):
    order_number: str
    customer_id: int
    warehouse_id: int
    order_date: date
    delivery_date: date
    total_weight_kg: Optional[float] = None
    total_volume_cubic_m: Optional[float] = None
    status: str = "Pending"
    priority: str = "Normal"
    cost: float
    notes: Optional[str] = None

    class Config:
        from_attributes = True
```

---

### API Endpoints

#### 📦 ЗАКАЗЫ (Orders)

```python
# GET - Получить все заказы
@app.get("/api/orders", tags=["Orders"])
def get_orders(status: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(OrderModel)
    if status:
        query = query.filter(OrderModel.status == status)
    return {
        "total": query.count(),
        "data": query.offset(skip).limit(limit).all()
    }

# POST - Создать новый заказ
@app.post("/api/orders", tags=["Orders"])
def create_order(order: OrderSchema, db: Session = Depends(get_db)):
    new_order = OrderModel(**order.dict())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return {
        "id": new_order.order_id,
        "message": "Заказ успешно создан",
        "order": new_order
    }

# GET - Получить заказ по ID
@app.get("/api/orders/{order_id}", tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order

# PUT - Обновить статус заказа
@app.put("/api/orders/{order_id}/status", tags=["Orders"])
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    order.status = status
    order.updated_at = datetime.utcnow()
    db.commit()
    return {"message": f"Статус заказа обновлен на {status}"}
```

#### 🚚 ДОСТАВКИ (Shipments)

```python
# GET - Получить все доставки
@app.get("/api/shipments", tags=["Shipments"])
def get_shipments(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ShipmentModel)
    if status:
        query = query.filter(ShipmentModel.status == status)
    return {
        "total": query.count(),
        "data": query.all()
    }

# POST - Создать новую доставку
@app.post("/api/shipments", tags=["Shipments"])
def create_shipment(shipment: ShipmentSchema, db: Session = Depends(get_db)):
    new_shipment = ShipmentModel(**shipment.dict())
    db.add(new_shipment)
    db.commit()
    db.refresh(new_shipment)
    return {
        "id": new_shipment.shipment_id,
        "message": "Доставка успешно создана"
    }

# PUT - Обновить статус доставки
@app.put("/api/shipments/{shipment_id}/status", tags=["Shipments"])
def update_shipment_status(shipment_id: int, status: str, db: Session = Depends(get_db)):
    shipment = db.query(ShipmentModel).filter(ShipmentModel.shipment_id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Доставка не найдена")
    shipment.status = status
    if status == "In Transit":
        shipment.departure_time = datetime.utcnow()
    elif status == "Delivered":
        shipment.actual_arrival_time = datetime.utcnow()
    shipment.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Статус доставки обновлен"}
```

#### 👥 КЛИЕНТЫ (Customers)

```python
# GET - Получить всех клиентов
@app.get("/api/customers", tags=["Customers"])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = db.query(CustomerModel).offset(skip).limit(limit).all()
    return {
        "total": db.query(CustomerModel).count(),
        "data": customers
    }

# POST - Создать клиента
@app.post("/api/customers", tags=["Customers"])
def create_customer(customer: CustomerSchema, db: Session = Depends(get_db)):
    new_customer = CustomerModel(**customer.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return {
        "id": new_customer.customer_id,
        "message": "Клиент успешно создан"
    }
```

#### 🚗 ВОДИТЕЛИ (Drivers)

```python
# GET - Получить доступных водителей
@app.get("/api/drivers", tags=["Drivers"])
def get_drivers(available_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(DriverModel)
    if available_only:
        query = query.filter(DriverModel.is_available == True)
    return {
        "total": query.count(),
        "data": query.all()
    }

# PUT - Обновить доступность водителя
@app.put("/api/drivers/{driver_id}/availability", tags=["Drivers"])
def update_driver_availability(driver_id: int, is_available: bool, db: Session = Depends(get_db)):
    driver = db.query(DriverModel).filter(DriverModel.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Водитель не найден")
    driver.is_available = is_available
    db.commit()
    return {"message": f"Водитель доступен: {is_available}"}
```

#### 📊 АНАЛИТИКА (Analytics)

```python
# GET - Доход и статистика
@app.get("/api/analytics/revenue", tags=["Analytics"])
def revenue_analytics(db: Session = Depends(get_db)):
    from sqlalchemy import func
    total_revenue = db.query(func.sum(OrderModel.cost)).scalar() or 0
    total_shipments = db.query(func.count(ShipmentModel.shipment_id)).scalar() or 0
    avg_shipment_cost = db.query(func.avg(ShipmentModel.cost)).scalar() or 0
    
    return {
        "total_revenue": float(total_revenue),
        "total_shipments": total_shipments,
        "average_shipment_cost": float(avg_shipment_cost)
    }

# GET - Производительность водителей
@app.get("/api/analytics/driver-performance", tags=["Analytics"])
def driver_performance(db: Session = Depends(get_db)):
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
```

#### ❤️ HEALTH CHECK

```python
@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

## 🎨 Frontend (HTML/JavaScript)

### Структура файла

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Система управления логистикой</title>
    <style>
        /* Стили */
    </style>
</head>
<body>
    <header>...</header>
    <nav>...</nav>
    <main>
        <div id="dashboard" class="tab-content active">...</div>
        <div id="orders" class="tab-content">...</div>
        <div id="shipments" class="tab-content">...</div>
        <div id="customers" class="tab-content">...</div>
        <div id="drivers" class="tab-content">...</div>
        <div id="vehicles" class="tab-content">...</div>
        <div id="analytics" class="tab-content">...</div>
    </main>
    <footer>...</footer>
    <script>
        // JavaScript код
    </script>
</body>
</html>
```

### Основные секции

#### 1. DASHBOARD (Главная страница)

Показывает статистику:
- Всего заказов
- Доставлено заказов
- В пути
- Доступных водителей
- Таблица последних заказов

```javascript
async function loadDashboard() {
    try {
        const ordersRes = await fetch(`${API_URL}/orders`);
        const ordersData = await ordersRes.json();
        
        const driversRes = await fetch(`${API_URL}/drivers?available_only=true`);
        const driversData = await driversRes.json();
        
        document.getElementById('stat-orders').textContent = ordersData.total;
        document.getElementById('stat-drivers').textContent = driversData.total;
        
        const delivered = ordersData.data.filter(o => o.status === 'Delivered').length;
        const inTransit = ordersData.data.filter(o => o.status === 'In Transit').length;
        
        document.getElementById('stat-delivered').textContent = delivered;
        document.getElementById('stat-in-transit').textContent = inTransit;
        
        // Заполнить таблицу
        const tbody = document.querySelector('table tbody');
        tbody.innerHTML = ordersData.data.slice(0, 5).map(order => `
            <tr>
                <td>${order.order_number}</td>
                <td>Customer ${order.customer_id}</td>
                <td><span class="badge ${order.status === 'Delivered' ? 'badge-success' : 'badge-pending'}">${order.status}</span></td>
                <td>${order.delivery_date}</td>
                <td>${order.cost}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Ошибка загрузки:', error);
        showAlert('Ошибка загрузки данных', 'danger');
    }
}
```

#### 2. ORDERS (Заказы)

- Таблица всех заказов
- Фильтр по статусу
- Кнопка "Новый заказ"
- Модальное окно добавления

```javascript
async function loadOrders() {
    try {
        const status = document.getElementById('order-status-filter')?.value;
        let url = `${API_URL}/orders`;
        if (status) url += `?status=${status}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        const tbody = document.querySelector('#orders-table tbody');
        tbody.innerHTML = data.data.map(order => `
            <tr>
                <td>${order.order_number}</td>
                <td>Customer ${order.customer_id}</td>
                <td><span class="badge ${order.status === 'Delivered' ? 'badge-success' : 'badge-pending'}">${order.status}</span></td>
                <td>${order.priority}</td>
                <td>${order.delivery_date}</td>
                <td>${order.cost}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

function openOrderModal() {
    document.getElementById('orderModal').classList.add('active');
    loadDropdowns();
}

function closeOrderModal() {
    document.getElementById('orderModal').classList.remove('active');
    document.getElementById('orderForm').reset();
}

async function saveOrder() {
    try {
        const formData = {
            order_number: document.getElementById('ordernumber').value,
            customer_id: parseInt(document.getElementById('customerid').value),
            warehouse_id: parseInt(document.getElementById('warehouseid').value || 1),
            order_date: new Date().toISOString().split('T')[0],
            delivery_date: document.getElementById('deliverydate').value,
            description: document.getElementById('description').value,
            priority: document.getElementById('priority').value,
            cost: parseFloat(document.getElementById('cost').value),
            status: 'Pending'
        };
        
        const response = await fetch(`${API_URL}/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showAlert('Заказ успешно создан!', 'success');
            closeOrderModal();
            loadOrders();
        } else {
            showAlert('Ошибка при создании', 'danger');
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
}
```

#### 3. SHIPMENTS (Доставки)

Управление партиями доставки с отслеживанием статуса

#### 4. CUSTOMERS (Клиенты)

Реестр клиентов с возможностью добавления новых

#### 5. DRIVERS (Водители)

Список водителей с информацией о лицензиях и рейтингах

#### 6. VEHICLES (Транспорт)

Реестр автомобилей с техническими характеристиками

#### 7. ANALYTICS (Аналитика)

```javascript
async function loadAnalytics() {
    try {
        const revenueRes = await fetch(`${API_URL}/analytics/revenue`);
        const revenueData = await revenueRes.json();
        
        document.getElementById('total-revenue').textContent = 
            Math.round(revenueData.total_revenue);
        document.getElementById('total-shipments').textContent = 
            revenueData.total_shipments;
        document.getElementById('avg-cost').textContent = 
            Math.round(revenueData.average_shipment_cost);
        
        const performanceRes = await fetch(`${API_URL}/analytics/driver-performance`);
        const performanceData = await performanceRes.json();
        
        const tbody = document.querySelector('#driver-performance-table tbody');
        tbody.innerHTML = performanceData.data.map(driver => `
            <tr>
                <td>${driver.name}</td>
                <td>${driver.deliveries}</td>
                <td>${driver.rating}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Ошибка:', error);
    }
}
```

### Стилизация (CSS)

```css
:root {
    --primary-color: #2563eb;
    --primary-dark: #1e40af;
    --secondary-color: #059669;
    --danger-color: #dc2626;
    --warning-color: #d97706;
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --bg-light: #f9fafb;
    --bg-white: #ffffff;
    --border-color: #e5e7eb;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: var(--bg-light);
    color: var(--text-primary);
    line-height: 1.6;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 20px;
}

header {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
    color: white;
    padding: 30px 0;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.card {
    background: var(--bg-white);
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    padding: 20px;
}

.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background: var(--primary-dark);
}

.btn-danger {
    background: var(--danger-color);
    color: white;
}

.table {
    width: 100%;
    border-collapse: collapse;
}

.table th {
    background: var(--bg-light);
    padding: 12px;
    text-align: left;
    font-weight: 600;
}

.table td {
    padding: 12px;
    border-bottom: 1px solid var(--border-color);
}

.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.badge-success {
    background: rgba(5, 150, 105, 0.1);
    color: var(--secondary-color);
}

.badge-pending {
    background: rgba(217, 119, 6, 0.1);
    color: var(--warning-color);
}

.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    align-items: center;
    justify-content: center;
}

.modal.active {
    display: flex;
}

.modal-content {
    background: var(--bg-white);
    border-radius: 8px;
    max-width: 600px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
}
```

---

## 🚀 Установка и запуск

### Требования

- Docker 20.10+
- Docker Compose 2.0+
- Git
- PostgreSQL 15+ (опционально, если не использовать Docker)

### Быстрый старт с Docker

```bash
# 1. Клонировать репозиторий
git clone https://github.com/ZybinIvan/database_project.git
cd database_project

# 2. Создать .env файл (опционально)
cp .env.example .env

# 3. Запустить контейнеры
docker-compose up -d --build

# 4. Проверить статус
docker-compose ps

# 5. Открыть в браузере
# API Docs:  http://localhost:8000/docs
# Web UI:    http://localhost:8001
# API:       http://localhost:8000/api
```

### Ручная установка без Docker

```bash
# 1. Установить зависимости Python
pip install -r requirements.txt

# 2. Создать БД PostgreSQL
createdb logistics_db
psql logistics_db < database_schema.sql

# 3. Заполнить данные
python populate_database.py

# 4. Запустить FastAPI сервер
python -m uvicorn fastapi_backend:app --host 0.0.0.0 --port 8000 --reload

# 5. Открыть фронтенд
# Скопируйте interface_web.html в веб-браузер или используйте простой HTTP сервер:
python -m http.server 8001
```

### Переменные окружения

```env
# .env файл
DB_HOST=postgres
DB_PORT=5432
DB_NAME=logistics_db
DB_USER=logistics
DB_PASSWORD=logistics_password
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=postgresql://logistics:logistics_password@postgres:5432/logistics_db
```

---

## 📡 Использование API

### Base URL
```
http://localhost:8000/api
```

### Аутентификация
API открыт без аутентификации (можно добавить JWT)

### Content-Type
```
application/json
```

---

## 📌 Примеры запросов

### 1. Получить все заказы

```bash
curl -X GET "http://localhost:8000/api/orders" \
  -H "Content-Type: application/json"
```

**Ответ:**
```json
{
    "total": 20,
    "data": [
        {
            "order_id": 1,
            "order_number": "ORD-2024-00001",
            "customer_id": 1,
            "warehouse_id": 1,
            "order_date": "2024-12-01",
            "delivery_date": "2024-12-10",
            "status": "Delivered",
            "priority": "Normal",
            "cost": 35000.00,
            "created_at": "2024-12-01T10:00:00"
        }
    ]
}
```

### 2. Создать новый заказ

```bash
curl -X POST "http://localhost:8000/api/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "ORD-2024-00021",
    "customer_id": 2,
    "warehouse_id": 1,
    "order_date": "2024-12-23",
    "delivery_date": "2024-12-30",
    "total_weight_kg": 150.5,
    "total_volume_cubic_m": 5.2,
    "status": "Pending",
    "priority": "High",
    "cost": 45000.00,
    "description": "Важная доставка"
  }'
```

**Ответ:**
```json
{
    "id": 21,
    "message": "Заказ успешно создан",
    "order": { ... }
}
```

### 3. Обновить статус заказа

```bash
curl -X PUT "http://localhost:8000/api/orders/1/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "Shipped"}'
```

или

```bash
curl -X PUT "http://localhost:8000/api/orders/1/status?status=Shipped"
```

### 4. Получить доставки по статусу

```bash
curl -X GET "http://localhost:8000/api/shipments?status=In%20Transit" \
  -H "Content-Type: application/json"
```

### 5. Создать доставку

```bash
curl -X POST "http://localhost:8000/api/shipments" \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_number": "SHIP-2024-00001",
    "order_id": 1,
    "vehicle_id": 1,
    "driver_id": 1,
    "route_id": 1,
    "status": "Pending",
    "cost": 5000.00
  }'
```

### 6. Получить аналитику

```bash
curl -X GET "http://localhost:8000/api/analytics/revenue" \
  -H "Content-Type: application/json"
```

**Ответ:**
```json
{
    "total_revenue": 700000.00,
    "total_shipments": 15,
    "average_shipment_cost": 46666.67
}
```

### 7. Получить производительность водителей

```bash
curl -X GET "http://localhost:8000/api/analytics/driver-performance" \
  -H "Content-Type: application/json"
```

**Ответ:**
```json
{
    "data": [
        {
            "driver_id": 1,
            "name": "Сергей Кузнецов",
            "deliveries": 5,
            "rating": 4.8
        },
        {
            "driver_id": 2,
            "name": "Елена Волкова",
            "deliveries": 4,
            "rating": 4.9
        }
    ]
}
```

### 8. Получить доступных водителей

```bash
curl -X GET "http://localhost:8000/api/drivers?available_only=true" \
  -H "Content-Type: application/json"
```

### 9. Получить всех клиентов

```bash
curl -X GET "http://localhost:8000/api/customers" \
  -H "Content-Type: application/json"
```

### 10. Создать клиента

```bash
curl -X POST "http://localhost:8000/api/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "ООО \"Новая Логистика\"",
    "contact_person": "Иван Иванов",
    "email": "ivan@newlogistics.ru",
    "phone": "+7-999-123-4567",
    "city": "Москва",
    "address": "ул. Новая, д. 10",
    "postal_code": "101000",
    "registration_date": "2024-12-23",
    "is_active": true
  }'
```

---

## 🐳 Docker Compose конфигурация

```yaml
version: '3.8'

services:
  # PostgreSQL База данных
  postgres:
    image: postgres:15-alpine
    container_name: logistics_postgres
    environment:
      POSTGRES_USER: logistics
      POSTGRES_PASSWORD: logistics_password
      POSTGRES_DB: logistics_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database_schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U logistics"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - logistics_network

  # FastAPI Backend
  api:
    build: .
    container_name: logistics_api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://logistics:logistics_password@postgres:5432/logistics_db
      API_HOST: 0.0.0.0
      API_PORT: 8000
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./fastapi_backend.py:/app/fastapi_backend.py
      - ./populate_database.py:/app/populate_database.py
    command: bash -c "python populate_database.py && python -m uvicorn fastapi_backend:app --host 0.0.0.0 --port 8000"
    networks:
      - logistics_network

  # Nginx Web Server
  web:
    image: nginx:alpine
    container_name: logistics_web
    ports:
      - "8001:80"
    volumes:
      - ./interface_web.html:/usr/share/nginx/html/index.html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
    networks:
      - logistics_network

networks:
  logistics_network:
    driver: bridge

volumes:
  postgres_data:
```

---

## 📂 Структура проекта

```
database_project/
├── fastapi_backend.py          # Основной API сервер
├── interface_web.html          # Веб-интерфейс (HTML+CSS+JS)
├── database_schema.sql         # SQL схема БД
├── populate_database.py        # Заполнение БД тестовыми данными
├── Dockerfile                  # Docker образ для API
├── docker-compose.yml          # Оркестрация контейнеров
├── nginx.conf                  # Конфиг Nginx
├── .dockerignore               # Исключения для Docker
├── .env.example                # Пример переменных окружения
├── Makefile                    # Удобные команды
├── requirements.txt            # Python зависимости
├── README.md                   # Основная документация
├── DOCKER.md                   # Docker документация
├── QUICK_START.md              # Быстрый старт
└── PROJECT_GUIDE.md           # Этот файл
```

---

## 🔧 Полезные команды

```bash
# Docker Compose
docker-compose up -d                    # Запустить контейнеры
docker-compose down                     # Остановить контейнеры
docker-compose logs -f                  # Просмотр логов
docker-compose ps                       # Статус контейнеров
docker-compose down -v                  # Удалить контейнеры и тома

# Makefile команды
make up                                 # docker-compose up -d
make down                               # docker-compose down
make logs                               # docker-compose logs -f
make restart                            # Перезагрузить контейнеры
make shell                              # bash в контейнере API
make db-shell                           # psql в PostgreSQL
make backup                             # Резервная копия БД
make restore FILE=backup.dump           # Восстановить БД

# Прямое подключение к БД
psql -h localhost -U logistics -d logistics_db -c "SELECT * FROM orders LIMIT 5;"

# Проверка здоровья API
curl http://localhost:8000/api/health

# Swagger документация
http://localhost:8000/docs
http://localhost:8000/redoc
```

---

## 📈 Масштабирование

### Добавление индексов

```sql
CREATE INDEX CONCURRENTLY idx_orders_status_date ON orders(status, order_date DESC);
CREATE INDEX CONCURRENTLY idx_shipments_driver_status ON shipments(driver_id, status);
```

### Кэширование

```python
from functools import lru_cache

@app.get("/api/analytics/summary", tags=["Analytics"])
@lru_cache(maxsize=32)
def get_analytics_summary(db: Session = Depends(get_db)):
    # Кэшированный результат
    pass
```

### Пагинация

```python
@app.get("/api/orders", tags=["Orders"])
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return {
        "total": db.query(OrderModel).count(),
        "skip": skip,
        "limit": limit,
        "data": db.query(OrderModel).offset(skip).limit(limit).all()
    }
```

---

## 🔒 Безопасность

### Добавить аутентификацию JWT

```python
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/login")
def login(username: str, password: str):
    # Проверка учетных данных
    token = jwt.encode({"sub": username}, "SECRET_KEY", algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}
```

### Rate limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/orders")
@limiter.limit("100/minute")
def get_orders(request: Request, db: Session = Depends(get_db)):
    pass
```

---

## 🐛 Troubleshooting

### Проблема: БД не подключается

```bash
# Проверить, запущен ли PostgreSQL
docker-compose ps postgres

# Проверить логи
docker-compose logs postgres

# Пересоздать контейнер
docker-compose down
docker-compose up -d --build
```

### Проблема: API возвращает 500 ошибку

```bash
# Смотреть логи API
docker-compose logs -f api

# Проверить подключение к БД
docker exec -it logistics_api python -c "import psycopg2; psycopg2.connect('postgresql://logistics:logistics_password@postgres:5432/logistics_db')"
```

### Проблема: Фронтенд не загружается

```bash
# Проверить доступность
curl http://localhost:8001

# Проверить логи Nginx
docker-compose logs -f web

# Проверить конфигурацию Nginx
docker exec logistics_web nginx -t
```

---

## 📝 Лицензия

MIT License - Используйте свободно

---

## 👨‍💻 Автор

**Ivan Zybin** - GitHub: https://github.com/ZybinIvan

---

## 📞 Контакты

- GitHub: https://github.com/ZybinIvan/database_project
- Issues: https://github.com/ZybinIvan/database_project/issues
- Email: (укажите ваш email)

---

**Последнее обновление:** 23 декабря 2025 г.

**Версия:** 1.0.0

**Статус:** Production Ready ✅
