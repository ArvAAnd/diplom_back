import sqlite3

db = sqlite3.connect('auth.db')

cursor = db.cursor()

cursor.execute("SELECT * FROM users")

# Извлечение результатов запроса
users = cursor.fetchall()

# Вывод результатов
for user in users:
    print("ID:", user[0])
    print("Username:", user[1])
    print("Password:", user[2])
    print("------------------")