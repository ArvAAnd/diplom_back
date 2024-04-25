import sqlite3

# Создание соединения с базой данных
db = sqlite3.connect('auth.db')

# Создание курсора
cursor = db.cursor()

# Создание таблицы пользователей
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    c TEXT
                )''')

db.commit()
db.close()