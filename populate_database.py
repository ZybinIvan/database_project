import psycopg2
from datetime import datetime, date, timedelta
import random
from decimal import Decimal

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'logistics_db',
    'user': 'logistics',
    'password': 'logistics_password'
}

print("🚚 Упрощенная система управления логистикой и доставкой")
print("📦 Скрипт заполнения БД реальными данными")
print("=" * 60)

EMPLOYEES_DATA = [
    ("Иван Петрович Семёнов", "Директор", "+7-911-111-1111", "2022-01-15"),
    ("Мария Александровна Козлова", "Менеджер", "+7-911-222-2222", "2021-06-10"),
    ("Сергей Иванович Беляев", "Водитель", "+7-911-333-3333", "2020-03-20"),
    ("Дмитрий Николаевич Соколов", "Водитель", "+7-911-444-4444", "2021-09-15"),
    ("Алексей Владимирович Новиков", "Водитель", "+7-911-555-5555", "2022-02-01"),
    ("Ольга Григорьевна Щербакова", "Менеджер склада", "+7-911-666-6666", "2021-01-10"),
    ("Николай Андреевич Федоров", "Водитель", "+7-911-777-7777", "2020-07-15"),
    ("Дарья Сергеевна Макарова", "Логист", "+7-911-888-8888", "2022-04-20"),
    ("Владимир Петрович Васильев", "Водитель", "+7-911-999-9999", "2021-03-12"),
    ("Андрей Михайлович Романов", "Водитель", "+7-911-101-0101", "2023-01-25"),
]

CUSTOMERS_DATA = [
    ("ООО \"Альфа Экспресс\"", "Петр Иванов", "+7-921-100-0001", "Москва", "ул. Тверская, д. 1"),
    ("ИП \"Бета Логистика\"", "Виктория Петрова", "+7-921-100-0002", "Санкт-Петербург", "Невский пр-т, д. 100"),
    ("ООО \"Гамма Торговля\"", "Юрий Сидоров", "+7-921-100-0003", "Москва", "Ленинский пр-т, д. 56"),
    ("ООО \"Дельта Импорт\"", "Анна Кузнецова", "+7-921-100-0004", "Екатеринбург", "ул. Малышева, д. 41"),
    ("ООО \"Эпсилон Дистрибьюция\"", "Михаил Волков", "+7-921-100-0005", "Новосибирск", "ул. Ленина, д. 200"),
    ("ООО \"Зета Курьер\"", "Валентина Морозова", "+7-921-100-0006", "Казань", "ул. Баумана, д. 76"),
    ("ООО \"Эта Перевозки\"", "Игорь Щербаков", "+7-921-100-0007", "Челябинск", "пр-т Ленина, д. 96"),
    ("ООО \"Тета Грузоперевозки\"", "Наташа Орлова", "+7-921-100-0008", "Омск", "ул. Маркса, д. 1"),
]

VEHICLES_DATA = [
    ("МТ123АА", "Car", "Toyota", "Camry", 200),
    ("МТ124АА", "Car", "BMW", "3 Series", 200),
    ("МТ200БВ", "Van", "Mercedes", "Sprinter", 2500),
    ("МТ201БВ", "Van", "Ford", "Transit", 2000),
    ("МТ300СС", "Truck", "Volvo", "FH16", 15000),
    ("МТ301СС", "Truck", "MAN", "TGX", 14000),
    ("МТ302СС", "Truck", "Scania", "R440", 16000),
    ("МТ400ДД", "Van", "Renault", "Master", 2200),
]

WAREHOUSES_DATA = [
    ("Московский склад", "Москва", "ул. Складская, д. 1", 1),
    ("Петербургский склад", "Санкт-Петербург", "Индустриальный пр-т, д. 50", 2),
    ("Центральный хаб", "Екатеринбург", "ул. Промышленная, д. 10", 6),
    ("Региональный пункт", "Новосибирск", "ул. Заводская, д. 5", 2),
]

ROUTES_DATA = [
    ("Москва - Тверь", "Москва", "Тверь", 170),
    ("Москва - Санкт-Петербург", "Москва", "Санкт-Петербург", 700),
    ("Москва - Екатеринбург", "Москва", "Екатеринбург", 1800),
    ("Москва - Казань", "Москва", "Казань", 815),
    ("Санкт-Петербург - Москва", "Санкт-Петербург", "Москва", 700),
    ("Москва - Новосибирск", "Москва", "Новосибирск", 3400),
    ("Москва - Челябинск", "Москва", "Челябинск", 2400),
    ("Москва - Омск", "Москва", "Омск", 2750),
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
                "INSERT INTO employee (full_name, position, phone, hire_date) VALUES (%s, %s, %s, %s)",
                data
            )
            print(f" ✓ Добавлен сотрудник: {data[0]}")
        except psycopg2.IntegrityError:
            conn.rollback()
            print(f" ⚠ Сотрудник {data[0]} уже существует")
        except Exception as e:
            conn.rollback()
            print(f" ✗ Ошибка при добавлении сотрудника {data[0]}: {e}")
    conn.commit()

def fill_customers(cursor, conn):
    print("\n📝 Заполнение таблицы клиентов...")
    for data in CUSTOMERS_DATA:
        try:
            cursor.execute(
                "INSERT INTO customer (company_name, contact_person, phone, city, address) VALUES (%s, %s, %s, %s, %s)",
                data
            )
            print(f" ✓ Добавлен клиент: {data[0]}")
        except psycopg2.IntegrityError:
            conn.rollback()
            print(f" ⚠ Клиент {data[0]} уже существует")
        except Exception as e:
            conn.rollback()
            print(f" ✗ Ошибка при добавлении клиента {data[0]}: {e}")
    conn.commit()

def fill_drivers(cursor, conn):
    print("\n📝 Заполнение таблицы водителей...")
    driver_data = [
        (3, "7712345678", 15),
        (4, "7798765432", 8),
        (5, "7723456789", 12),
        (7, "7734567890", 10),
        (9, "7745678901", 7),
        (10, "7756789012", 3),
    ]
    for data in driver_data:
        try:
            cursor.execute(
                "INSERT INTO driver (employee_id, license_number, experience_years) VALUES (%s, %s, %s)",
                data
            )
            cursor.execute("SELECT full_name FROM employee WHERE employee_id = %s", (data[0],))
            name = cursor.fetchone()[0]
            print(f" ✓ Добавлен водитель: {name} (ID {data[0]})")
        except psycopg2.IntegrityError:
            conn.rollback()
            print(f" ⚠ Водитель для сотрудника {data[0]} уже существует")
        except Exception as e:
            conn.rollback()
            print(f" ✗ Ошибка при добавлении водителя: {e}")
    conn.commit()

def fill_vehicles(cursor, conn):
    print("\n📝 Заполнение таблицы транспортных средств...")
    for data in VEHICLES_DATA:
        try:
            cursor.execute(
                "INSERT INTO vehicle (license_plate, vehicle_type, brand, model, capacity_kg) VALUES (%s, %s, %s, %s, %s)",
                data
            )
            print(f" ✓ Добавлено ТС: {data[1]} {data[2]} {data[3]} ({data[0]})")
        except psycopg2.IntegrityError:
            conn.rollback()
            print(f" ⚠ ТС с номером {data[0]} уже существует")
        except Exception as e:
            conn.rollback()
            print(f" ✗ Ошибка при добавлении ТС {data[0]}: {e}")
    conn.commit()

def fill_warehouses(cursor, conn):
    print("\n📝 Заполнение таблицы складов...")
    for data in WAREHOUSES_DATA:
        try:
            cursor.execute(
                "INSERT INTO warehouse (warehouse_name, city, address, manager_id) VALUES (%s, %s, %s, %s)",
                data
            )
            print(f" ✓ Добавлен склад: {data[0]}")
        except Exception as e:
            conn.rollback()
            print(f" ✗ Ошибка при добавлении склада {data[0]}: {e}")
    conn.commit()

def fill_routes(cursor, conn):
    print("\n📝 Заполнение таблицы маршрутов...")
    for data in ROUTES_DATA:
        try:
            cursor.execute(
                "INSERT INTO route (route_name, start_location, end_location, distance_km) VALUES (%s, %s, %s, %s)",
                data
            )
            print(f" ✓ Добавлен маршрут: {data[0]}")
        except Exception as e:
            conn.rollback()
            print(f" ✗ Ошибка при добавлении маршрута {data[0]}: {e}")
    conn.commit()

def fill_orders(cursor, conn):
    print("\n📝 Заполнение таблицы заказов...")
    statuses = ["Pending", "Processing", "In Transit", "Delivered"]
    for i in range(1, 21):
        try:
            order_number = f"ORD-2024-{i:05d}"
            customer_id = random.randint(1, len(CUSTOMERS_DATA))
            warehouse_id = random.randint(1, len(WAREHOUSES_DATA))
            order_date = date.today() - timedelta(days=random.randint(1, 30))
            delivery_date = order_date + timedelta(days=random.randint(3, 14))
            cost = Decimal(str(round(random.uniform(1000, 50000), 2)))
            cursor.execute(
                "INSERT INTO order_item (order_number, customer_id, warehouse_id, order_date, delivery_date, status, cost) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (order_number, customer_id, warehouse_id, order_date, delivery_date, random.choice(statuses), cost)
            )
            print(f" ✓ Добавлен заказ: {order_number}")
        except Exception as e:
            conn.rollback()
            print(f" ✗ Ошибка при добавлении заказа: {e}")
    conn.commit()

def fill_deliveries(cursor, conn):
    print("\n📝 Заполнение таблицы доставок...")
    statuses = ["Pending", "In Transit", "Delivered", "Failed"]
    for i in range(1, 21):
        try:
            delivery_number = f"DEL-2024-{i:05d}"
            order_id = random.randint(1, 20)
            vehicle_id = random.randint(1, len(VEHICLES_DATA))
            driver_id = random.randint(1, 6)
            route_id = random.randint(1, len(ROUTES_DATA))
            departure_time = datetime.now() - timedelta(days=random.randint(0, 10))
            delivery_time = departure_time + timedelta(hours=random.randint(4, 48))
            delivery_cost = Decimal(str(round(random.uniform(500, 10000), 2)))
            status = random.choice(statuses)
            final_delivery_time = delivery_time if status == "Delivered" else None
            cursor.execute(
                "INSERT INTO delivery (delivery_number, order_id, vehicle_id, driver_id, route_id, recipient_name, recipient_phone, recipient_address, departure_time, delivery_time, status, delivery_cost) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (delivery_number, order_id, vehicle_id, driver_id, route_id, f"Получатель #{i}", f"+7-921-{random.randint(100, 999)}-{random.randint(1000, 9999)}", f"ул. Приемная, д. {random.randint(1, 200)}", departure_time, final_delivery_time, status, delivery_cost)
            )
            print(f" ✓ Добавлена доставка: {delivery_number}")
        except Exception as e:
            conn.rollback()
            print(f" ✗ Ошибка при добавлении доставки: {e}")
    conn.commit()

def display_statistics(cursor):
    print("\n" + "=" * 60)
    print("📊 СТАТИСТИКА ЗАПОЛНЕННОЙ БД")
    print("=" * 60)
    tables = [
        ("employee", "Сотрудников"),
        ("customer", "Клиентов"),
        ("driver", "Водителей"),
        ("vehicle", "Транспортных средств"),
        ("warehouse", "Складов"),
        ("route", "Маршрутов"),
        ("order_item", "Заказов"),
        ("delivery", "Доставок"),
    ]
    for table, label in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f" {label}: {count}")
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
        fill_warehouses(cursor, conn)
        fill_routes(cursor, conn)
        fill_orders(cursor, conn)
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