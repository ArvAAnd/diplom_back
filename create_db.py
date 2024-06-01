import sqlite3


# Создание соединения с базой данных
db = sqlite3.connect('usersAndThemes.db')

# Создание курсора
cursor = db.cursor()

# Создание таблицы пользователей
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    gmail TEXT NOT NULL,
                    contacts TEXT,
                    rating INTEGER
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
cursor.execute('''CREATE TABLE IF NOT EXISTS rating_table(
                    id INTEGER PRIMARY KEY,
                    idUserRating INTEGER,
                    idUserRated INTEGER,
                    rating INTEGER,
                    FOREIGN KEY (idUserRating) REFERENCES users(id)
                    FOREIGN KEY (idUserRated) REFERENCES users(id)
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS tokens(
                    id INTEGER PRIMARY KEY,
                    token TEXT,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )''')

db.commit()
db.close()