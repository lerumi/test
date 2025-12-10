#!/usr/bin/env python3

import psycopg2
from psycopg2.extras import execute_batch
from random import random
from contextlib import closing

# Описание элементов ноутбуков
properties = {
    'manufacturers': ['LG', 'HP', 'Lenovo', 'Samsung', 'Asus', 'Acer', 'Apple'],
    'cpus': ['x64', 'ARM', 'RISC-V'],
    'harddrive_types': ['SSD', 'HDD', 'SSD+HDD'],
    'harddrive_spaces': ['<= 128 GB', '128-256GB', '256-512GB', '512-1024GB', '1024+GB'],
    'ram_types': ['DDR3', 'DDR4'],
    'rams': ['1-2GB', '2-4GB', '4-8GB', '8-16GB', '16+GB'],
    'wifis': ['No Wifi', 'Wifi 2.4', 'Wifi 5.8'],
    'bluetooths': ['No Bluetooth', 'Has Bluetooth'],
    'ethernets': ['No Ethernet', 'Has Ethernet'],
    'webcams': ['No Webcam', 'Has Webcam'],
    'cardreaders': ['No Cardreader', 'Has Cardreader'],
    'graphics': ['Integrated GPU', 'External GPU', 'Integrated+External GPU'],
    'displays': ['13.3 inch', '15.6 inch', '16 inch'],
    'usbs': ['No USB', 'USB 2.0', 'USB 3.0'],
    'batteries': ['<= 4 Hours', '4-6 hours', '6-8 hours', '8-10 hours', '10+ hours'],
}

# Определение длины вектора embedding
vector_len = 0
for p in properties.keys():
    vector_len += len(properties[p])

# Параметры подключения к PostgreSQL
DB_CONFIG = {
    'dbname': 'iu5',
    'user': 'postgres',
    'password': 'iu5-magisters',
    'host': 'localhost',
    'port': '5432'
}


# Функция для создания таблицы
def create_table():
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS laptops(
        id SERIAL PRIMARY KEY,
        manufacturer TEXT NOT NULL,
        cpu TEXT NOT NULL,
        harddrive_type TEXT NOT NULL,
        harddrive_space TEXT NOT NULL,
        ram_type TEXT NOT NULL,
        ram TEXT NOT NULL,
        wifi TEXT NOT NULL,
        bluetooth TEXT NOT NULL,
        ethernet TEXT NOT NULL,
        webcam TEXT NOT NULL,
        cardreader TEXT NOT NULL,
        graphics TEXT NOT NULL,
        display TEXT NOT NULL,
        usb TEXT NOT NULL,
        battery TEXT NOT NULL,
        embedding VECTOR({vector_len}) NOT NULL
    );
    """

    with closing(psycopg2.connect(**DB_CONFIG)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_table_sql)
            conn.commit()
            print("Таблица 'laptops' успешно создана или уже существует")


# Функция для генерации и вставки данных
def insert_data(num_configurations=500, batch_size=1000):
    data_to_insert = []

    for id in range(1, num_configurations + 1):
        embedding = []
        record = []

        for p in properties.keys():
            arr = properties[p]
            i = int(random() * len(arr))
            embedding += ['1' if j == i else '0' for j in range(len(arr))]
            record.append(arr[i])

        emb_text = '[' + (','.join(embedding)) + ']'
        record.append(emb_text)
        data_to_insert.append(tuple(record))

        # Вставка батчами
        if len(data_to_insert) >= batch_size:
            insert_batch(data_to_insert)
            data_to_insert = []
            print(f"Вставлено {min(id, num_configurations)} записей из {num_configurations}")

    # Вставка оставшихся записей
    if data_to_insert:
        insert_batch(data_to_insert)
        print(f"Вставлено {num_configurations} записей из {num_configurations}")


# Функция для пакетной вставки
def insert_batch(data):
    insert_sql = """
    INSERT INTO laptops (
        manufacturer, cpu, harddrive_type, harddrive_space,
        ram_type, ram, wifi, bluetooth, ethernet, webcam,
        cardreader, graphics, display, usb, battery, embedding
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    with closing(psycopg2.connect(**DB_CONFIG)) as conn:
        with conn.cursor() as cursor:
            execute_batch(cursor, insert_sql, data)
            conn.commit()


# Функция для проверки данных
def verify_data():
    with closing(psycopg2.connect(**DB_CONFIG)) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM laptops;")
            count = cursor.fetchone()[0]
            print(f"Всего записей в таблице: {count}")

            cursor.execute("SELECT * FROM laptops LIMIT 3;")
            sample = cursor.fetchall()
            print("\nПримеры записей (первые 3):")
            for row in sample:
                print(row[:5], "...")  # Показываем только первые 5 полей для краткости


# Основная функция
def main():
    print("Генерация данных для PostgreSQL...")

    # Создание таблицы
    create_table()

    # Вставка данных
    insert_data(num_configurations=500)  # Вместо 1_000_000 указано 500

    # Проверка данных
    verify_data()

    print("\nОперация завершена успешно!")


if __name__ == "__main__":
    main()