import sqlite3


# Создание соединения с базой данных
db = sqlite3.connect('usersAndThemes.db')

# Создание курсора
cursor = db.cursor()

# Создание таблицы пользователей
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS themes (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS user_expert_themes(
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    theme_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (theme_id) REFERENCES themes(id)
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS user_interested_themes(
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    theme_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (theme_id) REFERENCES themes(id)
                )''')

db.commit()
db.close()