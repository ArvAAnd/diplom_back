import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# def clear_table(table_name, db_file):
#     try:
#         # Устанавливаем соединение с базой данных
#         conn = sqlite3.connect(db_file)
#         cursor = conn.cursor()
#
#         # Выполняем SQL-запрос для удаления всех записей из таблицы
#         cursor.execute(f"DELETE FROM {table_name};")
#
#         # Фиксируем изменения в базе данных
#         conn.commit()
#
#         print(f"Таблица {table_name} в базе данных {db_file} очищена.")
#
#     except sqlite3.Error as e:
#         print("Ошибка SQLite:", e)
#
#     finally:
#         # Закрываем соединение с базой данных
#         if conn:
#             conn.close()

# @app.route('/clear_table', methods=['DELETE'])
# def clear_table_route():
#     clear_table('users', 'auth.db')

def get_connect():
    conn = sqlite3.connect('auth.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_user(username, password, c):
    with get_connect() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, password, c) VALUES (?, ?, ?)', (username, password, c))
        conn.commit()

def update_user(key, column, columnSource):
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute(f'UPDATE users SET {column} = ? WHERE id = ?', (columnSource, key))
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/update/c', methods=['POST'])
def update_user_route():

    dataJson = request.get_json()

    data = dataJson.get('data', '')
    key = data.get('id', '')
    c = data.get('c++', '')
    #print("dataJson = ", dataJson,"data = ", data, "key = ", key, "c++ = ", c)
    try:
        update_user(key, 'c', c)
        return jsonify({'message': 'Changed succesfully'})
    except Exception as e:
        print(e)
        return jsonify({'message': "Don't change"})

# Добавление пользователей
# users = [
#     ('user1', 'password1'),
#     ('user2', 'password2'),
#     ('user3', 'password3')
# ]
@app.route('/api/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Пользователь успешно удален'})

@app.route('/get_users', methods=['GET'])
def get_users_route():
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()

    # Вывод результатов
    users_list = [{'id': user['id'], 'name': user['name'], 'password': user['password'], 'c++': user['c']} for user in users]
    return jsonify(users_list)

    cursor.close()
    conn.close()

@app.route('/api/registration', methods=['POST'])
def registration():
    # Создание соединения с базой данных
    db = sqlite3.connect('auth.db')

    # Создание курсора
    cursor = db.cursor()

    dataJson = request.get_json()
    data = dataJson.get('data', '')
    username = data.get('name', '')
    password = data.get('password', '')
    c = data.get('c++', '')
    #print("c++ = ", c)
    try:
        # cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        add_user(username, password, c)

        cursor.execute("SELECT * FROM users")

        # Извлечение результатов запроса
        users = cursor.fetchall()

        # Вывод результатов
        for user in users:
            print("ID:", user[0])
            print("Username:", user[1])
            print("Password:", user[2])
            print("C++:", user[3])
            print("------------------")

        cursor.close()

        return jsonify({'user': dataJson})
    except sqlite3.IntegrityError:
        print(f"Пользователь с именем '{username}' уже существует. Пропускаем добавление.")
        return jsonify({'massage': 'Nevdalo'})
    db.close()





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# print("Таблица создана и заполнена данными.")