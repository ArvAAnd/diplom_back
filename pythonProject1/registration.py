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
    conn = sqlite3.connect('usersAndThemes.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_user(username, password):
    with get_connect() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, password) VALUES (?, ?)', (username, password))
        conn.commit()

# def update_user(key, column, columnSource):
#     conn = get_connect()
#     cursor = conn.cursor()
#     cursor.execute(f'UPDATE users SET {column} = ? WHERE id = ?', (columnSource, key))
#     conn.commit()
#     cursor.close()
#     conn.close()

# @app.route('/update/cPlus', methods=['POST'])
# def update_user_route():
#
#     dataJson = request.get_json()
#
#     data = dataJson.get('data', '')
#     key = data.get('id', '')
#     cPlus = data.get('c++', '')
#     #print("dataJson = ", dataJson,"data = ", data, "key = ", key, "c++ = ", c)
#     try:
#         update_user(key, 'cPlus', cPlus)
#         return jsonify({'message': 'Changed succesfully'})
#     except Exception as e:
#         print(e)
#         return jsonify({'message': "Don't change"})

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

@app.route('/delete_expert_and_interested/<int:user_id>', methods=['DELETE'])
def delete_expert_and_interested(user_id):
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_expert_themes WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM user_interested_themes WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Пользователь успешно удален'})

# @app.route('/delete_interested/<int:user_id>', methods=['DELETE'])
# def delete_interested(user_id):
#     conn = get_connect()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM user_interested_themes WHERE user_id = ?", (user_id,))
#     conn.commit()
#     conn.close()
#     return jsonify({'message': 'Пользователь успешно удален'})

@app.route('/get_users', methods=['GET'])
def get_users_route():
    conn = get_connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_expert_themes")
    experts = cursor.fetchall()

    cursor.execute("SELECT * FROM user_interested_themes")
    interesteds = cursor.fetchall()

    cursor.execute("SELECT * FROM themes")
    themes = cursor.fetchall()

    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()



    # Вывод результатов
    users_list = [{
        'id': user['id'],
        'name': user['name'],
        'password': user['password'],
        'experts': [[theme['name']] for theme in themes if theme['id'] in [expert[2] for expert in experts if expert[1] == user['id']]],
        'interests': [[theme['name']] for theme in themes if theme['id'] in [interested[2] for interested in interesteds if interested[1] == user['id']]]}
        for user in users]
    cursor.close()
    conn.close()
    return jsonify(users_list)



@app.route('/get_themes', methods=['GET'])
def get_themes_route():
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM themes")
    themes = cursor.fetchall()

    themes_list = [{'id': theme['id'], 'name': theme['name']} for theme in themes]
    cursor.close()
    conn.close()
    return jsonify(themes_list)


# @app.route('/get_experts', methods=['GET'])
# def get_experts_route():
#     conn = get_connect()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM user_expert_themes")
#     experts = cursor.fetchall()
#
#     experts_list = [{'id': expert['id'], 'user_id': expert['user_id'], 'theme_id': expert['theme_id']} for expert in experts]
#     cursor.close()
#     conn.close()
#     return jsonify(experts_list)

# @app.route('/get_interesteds', methods=['GET'])
# def get_interesteds_route():
#     conn = get_connect()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM user_interested_themes")
#     interesteds = cursor.fetchall()
#
#     interesteds_list = [{'id': interested['id'], 'user_id': interested['user_id'], 'theme_id': interested['theme_id']} for interested in interesteds]
#     cursor.close()
#     conn.close()
#     return jsonify(interesteds_list)

@app.route('/api/registration', methods=['POST'])
def registration():
    # Создание соединения с базой данных
    db = sqlite3.connect('usersAndThemes.db')

    # Создание курсора
    cursor = db.cursor()

    dataJson = request.get_json()
    data = dataJson.get('data', '')
    username = data.get('name', '')
    password = data.get('password', '')
    #print("c++ = ", c)
    try:
        # cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        add_user(username, password)

        cursor.execute("SELECT * FROM users")

        # Извлечение результатов запроса
        users = cursor.fetchall()

        # Вывод результатов
        for user in users:
            print("ID:", user[0])
            print("Username:", user[1])
            print("Password:", user[2])
            print("------------------")

        cursor.close()
        last_user = users[len(users) - 1]
        return jsonify({'id': last_user[0], 'name': last_user[1], 'password': last_user[2]})
    except sqlite3.IntegrityError:
        print(f"Пользователь с именем '{username}' уже существует. Пропускаем добавление.")
        return jsonify({'massage': 'Nevdalo'})
    db.close()

def user_get_expert_themes(user_id, theme_id):
    with get_connect() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user_expert_themes (user_id, theme_id) VALUES (?, ?)', (user_id, theme_id))
        conn.commit()

def user_get_interested_themes(user_id, theme_id):
    with get_connect() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user_interested_themes (user_id, theme_id) VALUES (?, ?)', (user_id, theme_id))
        conn.commit()

def add_theme(nameTheme):
    with get_connect() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO themes (name) VALUES (?)', (nameTheme,))
        conn.commit()

@app.route('/add-theme', methods=['POST'])
def add_theme_route():
    dataJson = request.get_json()
    data = dataJson.get('data', '')
    name = data.get('name', '')
    print(name)
    try:
        add_theme(name)

        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM themes")

        # Извлечение результатов запроса
        themes = cursor.fetchall()

        # Вывод результатов
        for theme in themes:
            print("ID:", theme[0])
            print("name:", theme[1])
            print("------------------")

        cursor.close()
        conn.close()

        return jsonify({'message': 'Add theme'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Cant add theme'})

@app.route('/stay_expert_and_interested', methods=['POST'])
def user_expert_interested_themes_route():
    dataJson = request.get_json()

    data = dataJson.get('data', '')
    changeMode = data.get('changeMode', '')
    user_id = data.get('user_id', '')
    themesExpert = data.get('themesIdExpert', '')
    themesInterested = data.get('themesIdInterested', '')
    try:
        if(user_id != 0 and (themesExpert!=[] or themesInterested!=[])):
            conn = get_connect()
            cursor = conn.cursor()
            if (changeMode == 'true'):
                cursor.execute("DELETE FROM user_expert_themes WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM user_interested_themes WHERE user_id = ?", (user_id,))
            if(themesExpert!=[]):
                [user_get_expert_themes(user_id, theme_id) for theme_id in themesExpert]
            if(themesInterested!=[]):
                [user_get_interested_themes(user_id, theme_id) for theme_id in themesInterested]

            cursor.execute("SELECT * FROM user_expert_themes")

        # Извлечение результатов запроса
            user_expert_themes = cursor.fetchall()

        # Вывод результатов
            for expert in user_expert_themes:
                print("ID user:", expert[1])
                print("ID theme:", expert[2])
                print("------------------")

            cursor.close()
            conn.close()
            return jsonify({'message': 'Succesful stay expert and interested'})
        else:
            return jsonify({'message': 'Cant stay expert or interested'})

    except:
        return jsonify({'message': 'Cant stay expert'})

# @app.route('/stay_interested', methods=['POST'])
# def user_interested_themes_route():
#     dataJson = request.get_json()
#
#     data = dataJson.get('data', '')
#     user_id = data.get('user_id', '')
#     theme_id = data.get('theme_id', '')
#     try:
#         if(user_id != 0 and theme_id!=0):
#             user_get_interested_themes(user_id, theme_id)
#
#             conn = get_connect()
#             cursor = conn.cursor()
#             cursor.execute("SELECT * FROM user_interested_themes")
#
#             # Извлечение результатов запроса
#             user_interested_themes = cursor.fetchall()
#
#             # Вывод результатов
#             for interested in user_interested_themes:
#                 print("ID user:", interested[1])
#                 print("ID theme:", interested[2])
#                 print("------------------")
#
#             cursor.close()
#             conn.close()
#             last_interested = user_interested_themes[len(user_interested_themes) - 1]
#             return jsonify({'user_id': last_interested[1], 'theme_id': last_interested[2]})
#         else:
#             return jsonify({'message': 'Cant stay interested'})
#
#     except:
#         return jsonify({'message': 'Cant stay expert'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# print("Таблица создана и заполнена данными.")