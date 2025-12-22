import psycopg2
from datetime import datetime, date, timedelta
import random
from decimal import Decimal

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'logistics_db',
    'user': 'logistics',
    'password': 'logistics_password'
}

print("🚚 Информационная система управления логистикой и доставкой")
print("📦 Скрипт заполнения БД реальными данными")
print("=" * 60)

# Sample data
EMPLOYEES_DATA = [
    ("Иван Петров", "Директор", "ivan.petrov@logistics.ru", "+7-911-111-1111", "2022-01-15", 75000),
    ("Мария Сидорова", "Менеджер", "maria.sidorova@logistics.ru", "+7-911-222-2222", "2021-06-10", 65000),
    ("Сергей Кузнецов", "Водитель", "sergey.kuznetsov@logistics.ru", "+7-911-333-3333", "2020-03-20", 55000),
    ("Елена Волкова", "Водитель", "elena.volkova@logistics.ru", "+7-911-444-4444", "2021-09-15", 55000),
    ("Алексей Морозов", "Водитель", "alexey.morozov@logistics.ru", "+7-911-555-5555", "2022-02-01", 55000),
    ("Ольга Щербакова", "Менеджер склада", "olga.shcherbakova@logistics.ru", "+7-911-666-6666", "2021-01-10", 60000),
    ("Николай Орлов", "Водитель", "nikolay.orlov@logistics.ru", "+7-911-777-7777", "2020-07-15", 55000),
    ("Дарья Попова", "Логист", "darya.popova@logistics.ru", "+7-911-888-8888", "2022-04-20", 50000),
]

CUSTOMERS_DATA = [
    ("ООО \"Альфа Экспресс\"", "Петр Иванов", "petr@alpha.ru", "+7-921-100-0001", "Москва", "ул. Тверская, д. 1", "101000"),
    ("ИП \"Бета Логистика\"", "Виктория Петрова", "victoria@beta.ru", "+7-921-100-0002", "Санкт-Петербург", "Невский пр-т, д. 100", "191000"),
    ("ООО \"Гамма Торговля\"", "Юрий Сидоров", "yury@gamma.ru", "+7-921-100-0003", "Москва", "Ленинский пр-т, д. 56", "117485"),
    ("ООО \"Дельта Импорт\"", "Анна Кузнецова", "anna@delta.ru", "+7-921-100-0004", "Екатеринбург", "ул. Малышева, д. 41", "620014"),
    ("ООО \"Эпсилон Дистрибьюция\"", "Михаил Волков", "mikhail@epsilon.ru", "+7-921-100-0005", "Новосибирск", "ул. Ленина, д. 200", "630099"),
    ("ООО \"Зета Курьер\"", "Валентина Морозова", "valentina@zeta.ru", "+7-921-100-0006", "Казань", "ул. Баумана, д. 76", "420111"),
    ("ООО \"Эта Перевозки\"", "Игорь Щербаков", "igor@eta.ru", "+7-921-100-0007", "Челябинск", "пр-т Ленина, д. 96", "454081"),
    ("ООО \"Тета Грузоперевозки\"", "Наташа Орлова", "natasha@theta.ru", "+7-921-100-0008", "Омск", "ул. Маркса, д. 1", "644043"),
]

VEHICLES_DATA = [
    ("МТ123АА", "Car", "Toyota", "Camry", 2022, 200, 0.5),
    ("МТ124АА", "Car", "BMW", "3 Series", 2023, 200, 0.5),
    ("МТ200БВ", "Van", "Mercedes", "Sprinter", 2021, 2500, 12),
    ("МТ201БВ", "Van", "Ford", "Transit", 2022, 2000, 10),
    ("МТ300СС", "Truck", "Volvo", "FH16", 2020, 15000, 65),
    ("МТ301СС", "Truck", "MAN", "TGX", 2021, 14000, 60),
    ("МТ302СС", "Truck", "Scania", "R440", 2022, 16000, 70),
    ("МТ400ДД", "Van", "Renault", "Master", 2023, 2200, 11),
]

# ВАЖНО: Исправлено кол-во элементов в каждом кортеже (7 элементов)
WAREHOUSES_DATA = [
    ("Московский склад", "Москва", "ул. Складская, д. 1", "127254", 1, 10000, "+7-921-100-1001"),
    ("Петербургский склад", "Санкт-Петербург", "Индустриальный пр-т, д. 50", "191123", 2, 8000, "+7-921-100-1002"),
    ("Центральный хаб", "Екатеринбург", "ул. Промышленная, д. 10", "170100", 6, 15000, "+7-921-100-1003"),
    ("Региональный пункт", "Новосибирск", "ул. Заводская, д. 5", "214018", 2, 5000, "+7-921-100-1004"),
]

ROUTES_DATA = [
    ("Москва - Тверь", "Москва", "Тверь", 170, 2.5),
    ("Москва - Санкт-Петербург", "Москва", "Санкт-Петербург", 700, 10),
    ("Москва - Екатеринбург", "Москва", "Екатеринбург", 1800, 24),
    ("Москва - Казань", "Москва", "Казань", 815, 11),
    ("Санкт-Петербург - Москва", "Санкт-Петербург", "Москва", 700, 10),
    ("Москва - Новосибирск", "Москва", "Новосибирск", 3400, 48),
    ("Москва - Челябинск", "Москва", "Челябинск", 2400, 32),
    ("Москва - Омск", "Москва", "Омск", 2750, 38),
]

def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Подключение к БД успешно\n")
        return conn
    except psycopg2.Error as e:
        print(f"✗ Ошибка подключения: {e}")
        return None

def fill_employees(cursor, conn):
    print("📝 Заполнение таблицы сотрудников...")
    for data in EMPLOYEES_DATA:
        try:
            cursor.execute(
                "INSERT INTO employees (full_name, position, email, phone, hire_date, salary) VALUES (%s, %s, %s, %s, %s, %s)",
                data
            )
            print(f"  ✓ Добавлен сотрудник: {data[0]}")
        except psycopg2.IntegrityError:
            conn.rollback()
            print(f"  ⚠ Сотрудник {data[0]} уже существует")
        except Exception as e:
            conn.rollback()
            print(f"  ✗ Ошибка при добавлении сотрудника {data[0]}: {e}")
    conn.commit()

def fill_customers(cursor, conn):
    print("\n📝 Заполнение таблицы клиентов...")
    for data in CUSTOMERS_DATA:
        try:
            cursor.execute(
                "INSERT INTO customers (company_name, contact_person, email, phone, city, address, postal_code, registration_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (*data, date.today())
            )
            print(f"  ✓ Добавлен клиент: {data[0]}")
        except psycopg2.IntegrityError:
            conn.rollback()
            print(f"  ⚠ Клиент {data[0]} уже существует")
        except Exception as e:
            conn.rollback()
            print(f"  ✗ Ошибка при добавлении клиента {data[0]}: {e}")
    conn.commit()

def fill_drivers(cursor, conn):
    print("\n📝 Заполнение таблицы водителей...")
    driver_data = [
        (3, "123456", date(2025, 12, 31), 15),
        (4, "654321", date(2024, 8, 15), 8),
        (5, "111222", date(2026, 3, 20), 12),
        (7, "333444", date(2025, 6, 10), 10),
    ]
    for data in driver_data:
        try:
            cursor.execute(
                "INSERT INTO drivers (employee_id, license_number, license_expiry_date, experience_years) VALUES (%s, %s, %s, %s)",
                data
            )
            print(f"  ✓ Добавлен водитель для сотрудника ID {data[0]}")
        except psycopg2.IntegrityError:
            conn.rollback()
            print(f"  ⚠ Водитель для сотрудника {data[0]} уже существует")
        except Exception as e:
            conn.rollback()
            print(f"  ✗ Ошибка при добавлении водителя: {e}")
    conn.commit()

def fill_vehicles(cursor, conn):
    print("\n📝 Заполнение таблицы транспортных средств...")
    for data in VEHICLES_DATA:
        try:
            cursor.execute(
                "INSERT INTO vehicles (license_plate, vehicle_type, brand, model, year, capacity_kg, capacity_cubic_m, mileage, last_maintenance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (*data, random.randint(5000, 100000), date.today() - timedelta(days=random.randint(1, 90)))
            )
            print(f"  ✓ Добавлено ТС: {data[1]} {data[2]} {data[3]}")
        except psycopg2.IntegrityError:
            conn.rollback()
            print(f"  ⚠ ТС с номером {data[0]} уже существует")
        except Exception as e:
            conn.rollback()
            print(f"  ✗ Ошибка при добавлении ТС {data[0]}: {e}")
    conn.commit()

def fill_warehouses(cursor, conn):
    print("\n📝 Заполнение таблицы складов...")
    for data in WAREHOUSES_DATA:
        try:
            # data = (name, city, address, postal_code, manager_id, capacity, phone) - 7 элементов
            cursor.execute(
                "INSERT INTO warehouses (warehouse_name, city, address, postal_code, manager_id, capacity_items, current_items, phone, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    data[0],                                  # warehouse_name
                    data[1],                                  # city
                    data[2],                                  # address
                    data[3],                                  # postal_code
                    data[4],                                  # manager_id
                    data[5],                                  # capacity_items
                    random.randint(100, int(data[5] * 0.8)), # current_items (случайное значение)
                    data[6],                                  # phone
                    f"warehouse{data[4]}@logistics.ru"        # email
                )
            )
            print(f"  ✓ Добавлен склад: {data[0]}")
        except Exception as e:
            conn.rollback()
            print(f"  ✗ Ошибка при добавлении склада {data[0]}: {e}")
    conn.commit()

def fill_routes(cursor, conn):
    print("\n📝 Заполнение таблицы маршрутов...")
    for data in ROUTES_DATA:
        try:
            cursor.execute(
                "INSERT INTO delivery_routes (route_name, start_location, end_location, distance_km, estimated_duration_hours) VALUES (%s, %s, %s, %s, %s)",
                data
            )
            print(f"  ✓ Добавлен маршрут: {data[0]}")
        except Exception as e:
            conn.rollback()
            print(f"  ✗ Ошибка при добавлении маршрута {data[0]}: {e}")
    conn.commit()

def fill_orders(cursor, conn):
    print("\n📝 Заполнение таблицы заказов...")
    statuses = ["Pending", "Processing", "Shipped", "Delivered"]
    priorities = ["Low", "Normal", "High", "Urgent"]

    for i in range(1, 21):
        try:
            order_number = f"ORD-2024-{i:05d}"
            customer_id = random.randint(1, len(CUSTOMERS_DATA))
            warehouse_id = random.randint(1, len(WAREHOUSES_DATA))
            order_date = date.today() - timedelta(days=random.randint(1, 30))
            delivery_date = order_date + timedelta(days=random.randint(3, 14))
            weight = Decimal(str(round(random.uniform(10, 500), 2)))
            volume = Decimal(str(round(random.uniform(0.1, 20), 2)))
            cost = Decimal(str(round(random.uniform(1000, 50000), 2)))

            cursor.execute(
                "INSERT INTO orders (order_number, customer_id, warehouse_id, order_date, delivery_date, total_weight_kg, total_volume_cubic_m, status, priority, cost, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (order_number, customer_id, warehouse_id, order_date, delivery_date, weight, volume, random.choice(statuses), random.choice(priorities), cost, f"Заказ #{i}")
            )
            print(f"  ✓ Добавлен заказ: {order_number}")
        except Exception as e:
            conn.rollback()
            print(f"  ✗ Ошибка при добавлении заказа: {e}")
    conn.commit()

def fill_shipments(cursor, conn):
    print("\n📝 Заполнение таблицы партий доставки...")
    statuses = ["Pending", "In Transit", "Delivered", "Delayed"]

    for i in range(1, 16):
        try:
            shipment_number = f"SHIP-2024-{i:05d}"
            order_id = random.randint(1, 20)
            vehicle_id = random.randint(1, len(VEHICLES_DATA))
            driver_id = random.randint(1, 4)
            route_id = random.randint(1, len(ROUTES_DATA))
            departure_time = datetime.now() - timedelta(days=random.randint(0, 10))
            expected_arrival = departure_time + timedelta(hours=random.randint(4, 48))
            actual_arrival = expected_arrival + timedelta(hours=random.randint(-2, 6))
            distance_traveled = Decimal(str(round(random.uniform(50, 1800), 2)))
            fuel_consumed = Decimal(str(round(random.uniform(5, 200), 2)))
            cost = Decimal(str(round(random.uniform(500, 10000), 2)))

            cursor.execute(
                "INSERT INTO shipments (shipment_number, order_id, vehicle_id, driver_id, route_id, departure_time, expected_arrival_time, actual_arrival_time, status, distance_traveled_km, fuel_consumed_liters, cost) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (shipment_number, order_id, vehicle_id, driver_id, route_id, departure_time, expected_arrival, actual_arrival, random.choice(statuses), distance_traveled, fuel_consumed, cost)
            )
            print(f"  ✓ Добавлена партия: {shipment_number}")
        except Exception as e:
            conn.rollback()
            print(f"  ✗ Ошибка при добавлении партии: {e}")
    conn.commit()

def fill_deliveries(cursor, conn):
    print("\n📝 Заполнение таблицы доставок...")
    statuses = ["Pending", "In Transit", "Delivered", "Failed", "Reattempt"]
    cities = ["Москва", "Тверь", "Санкт-Петербург", "Екатеринбург", "Казань", "Новосибирск", "Челябинск", "Омск"]

    for i in range(1, 21):
        try:
            shipment_id = random.randint(1, 15)
            recipient_name = f"Получатель #{i}"
            recipient_phone = f"+7-921-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            recipient_address = f"ул. Приемная, д. {random.randint(1, 200)}"
            recipient_city = random.choice(cities)
            status = random.choice(statuses)
            delivery_time = datetime.now() - timedelta(days=random.randint(0, 30)) if status == "Delivered" else None
            signature_required = random.choice([True, False])
            attempts = random.randint(0, 2)

            cursor.execute(
                "INSERT INTO deliveries (shipment_id, recipient_name, recipient_phone, recipient_address, recipient_city, delivery_time, signature_required, status, attempts) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (shipment_id, recipient_name, recipient_phone, recipient_address, recipient_city, delivery_time, signature_required, status, attempts)
            )
            print(f"  ✓ Добавлена доставка #{i}")
        except Exception as e:
            conn.rollback()
            print(f"  ✗ Ошибка при добавлении доставки: {e}")
    conn.commit()

def display_statistics(cursor):
    print("\n" + "=" * 60)
    print("📊 СТАТИСТИКА ЗАПОЛНЕННОЙ БД")
    print("=" * 60)

    tables = [
        ("employees", "Сотрудников"),
        ("customers", "Клиентов"),
        ("drivers", "Водителей"),
        ("vehicles", "Транспортных средств"),
        ("warehouses", "Складов"),
        ("delivery_routes", "Маршрутов"),
        ("orders", "Заказов"),
        ("shipments", "Партий доставки"),
        ("deliveries", "Доставок"),
    ]

    for table, label in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {label}: {count}")

    print("=" * 60)

def main():
    print()
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()

    try:
        fill_employees(cursor, conn)
        fill_customers(cursor, conn)
        fill_drivers(cursor, conn)
        fill_vehicles(cursor, conn)
        fill_warehouses(cursor, conn)  # ИСПРАВЛЕНО
        fill_routes(cursor, conn)
        fill_orders(cursor, conn)
        fill_shipments(cursor, conn)
        fill_deliveries(cursor, conn)

        display_statistics(cursor)

        print("\n✅ ВСЕ ДАННЫЕ УСПЕШНО ЗАГРУЖЕНЫ В БД!")

    except Exception as e:
        print(f"✗ Критическая ошибка: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
