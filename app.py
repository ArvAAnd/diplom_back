import sqlite3
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import secrets
from collections import Counter

app = Flask(__name__)
CORS(app)
logging.basicConfig(level = logging.DEBUG)

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

def get_tables():
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_expert_themes")
    experts = cursor.fetchall()

    cursor.execute("SELECT * FROM user_interested_themes")
    interesteds = cursor.fetchall()

    cursor.execute("SELECT * FROM themes")
    themes = cursor.fetchall()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.close()
    conn.close()
    return [experts, interesteds, themes, users]

def add_user(username, password, gmail):
    with get_connect() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, password, gmail) VALUES (?, ?, ?)', (username, password, gmail))
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
    cursor.execute("DELETE FROM user_expert_themes WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM user_interested_themes WHERE user_id = ?", (user_id,))
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
        'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [expert[2] for expert in experts if expert[1] == user['id']]],
        'interests': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [interested[2] for interested in interesteds if interested[1] == user['id']]]}
        for user in users]
    cursor.close()
    conn.close()
    return jsonify(users_list)



@app.route('/get_themes', methods=['GET'])
def get_themes_route():
    tables = get_tables()
    themes = tables[2]

    themes_list = [{'id': theme['id'], 'name': theme['name']} for theme in themes]
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

    dataJson = request.get_json()
    data = dataJson.get('data', '')
    username = data.get('name', '')
    password = data.get('password', '')
    gmail = data.get('gmail', '')
    #print("c++ = ", c)
    try:
        # cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        add_user(username, password, gmail)

        tables = get_tables()
        experts = tables[0]

        interesteds = tables[1]

        themes = tables[2]

        users = tables[3]


        last_user = users[len(users) - 1]

        user_list = {
            'id': last_user['id'],
            'name': last_user['name'],
            'password': last_user['password'],
            'gmail': last_user['gmail'],
            'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [expert[2] for expert in experts if expert[1] == last_user['id']]],
            'interests': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [interested[2] for interested in interesteds if interested[1] == last_user['id']]]}
        #'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [expert[2] for expert in experts if expert[1] == user['id']]],
        #'interests': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [interested[2] for interested in interesteds if interested[1] == user['id']]]}


        tocken = secrets.token_urlsafe()
        return jsonify({'data':user_list, 'tocken':tocken})
    except sqlite3.IntegrityError:
        print(f"Пользователь с именем '{username}' уже существует. Пропускаем добавление.")
        return jsonify({'massage': 'Nevdalo'})


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

        tables = get_tables()
        themes = tables[2]

        # Вывод результатов
        for theme in themes:
            print("ID:", theme[0])
            print("name:", theme[1])
            print("------------------")

        return jsonify({'message': 'Add theme'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Cant add theme'})

@app.route('/stay_expert_and_interested', methods=['POST'])
def user_expert_interested_themes_route():
    dataJson = request.get_json()
    data = dataJson.get('data', '')
    #print(data)
    changeMode = data.get('changeMode', '')
    user_id = data.get('user_id', '')
    themesExpert = data.get('themesIdExpert', '')
    themesInterested = data.get('themesIdInterested', '')

    try:
        if(user_id != 0 and (themesExpert!=[] or themesInterested!=[])):


            if (changeMode == True):
                with get_connect() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM user_expert_themes WHERE user_id = ?", (user_id,))
                    cursor.execute("DELETE FROM user_interested_themes WHERE user_id = ?", (user_id,))
            if(themesExpert!=[]):
                [user_get_expert_themes(user_id, theme_id) for theme_id in themesExpert]
            if(themesInterested!=[]):
                [user_get_interested_themes(user_id, theme_id) for theme_id in themesInterested]

            tables = get_tables()
            experts = tables[0]
            themes = tables[2]
            interesteds = tables[1]

            # Вывод результатов
            #     for expert in user_expert_themes:
            #         print("ID user:", expert[1])
            #         print("ID theme:", expert[2])
            #         print("------------------")
            return jsonify({'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [expert[2] for expert in experts if expert[1] == user_id]],
                            'interesteds': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [interested[2] for interested in interesteds if interested[1] == user_id]]})
        else:
            return jsonify({'message': 'Cant stay expert or interested'})

    except Exception as e:
        print(e)
        return jsonify({'message': 'Cant stay expert'})

@app.route('/authorization', methods=['POST'])
def authorization():
    try:
        dataJson = request.get_json()
        data = dataJson.get('data', '')
        name = data.get('name', '')
        password = data.get('password', '')
        #print(name, password)

        tables = get_tables()
        users = tables[3]
        themes = tables[2]
        interesteds = tables[1]
        experts = tables[0]
        authoriz_user = [user for user in users if user['name'] == name and user['password'] == password][0]

        user_list = {
            'id': authoriz_user['id'],
            'name': authoriz_user['name'],
            'password': authoriz_user['password'],
            'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if
                        theme['id'] in [expert[2] for expert in experts if expert[1] == authoriz_user['id']]],
            'interests': [{'id': theme['id'], 'name': theme['name']} for theme in themes if
                          theme['id'] in [interested[2] for interested in interesteds if interested[1] == authoriz_user['id']]]}

        tocken = secrets.token_urlsafe()
        return jsonify({'data': user_list, 'tocken': tocken})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Failed autorization'})

@app.route('/read_token', methods=['POST'])
def read_token():

    try:
        data = request.get_json()
        #print(data)
        idUser = data.get('id', '')
        #print(idUser)


        tables = get_tables()
        experts = tables[0]

        interesteds = tables[1]

        themes = tables[2]

        users = tables[3]

        token_user = [user for user in users if user['id'] == idUser][0]

        user_list = {
            'id': token_user['id'],
            'name': token_user['name'],
            'password': token_user['password'],
            'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if
                        theme['id'] in [expert[2] for expert in experts if expert[1] == token_user['id']]],
            'interests': [{'id': theme['id'], 'name': theme['name']} for theme in themes if
                          theme['id'] in [interested[2] for interested in interesteds if
                                          interested[1] == token_user['id']]]}
        return jsonify(user_list)
    except Exception as e:
        print(e)
        return jsonify({'message': 'Failed autorization'})

@app.route('/one_user/<int:user_id>', methods=['GET'])
def one_user(user_id):

    try:
        idUser = user_id


        tables = get_tables()

        experts = tables[0]

        interesteds = tables[1]

        themes = tables[2]

        users = tables[3]

        user_by_id = [user for user in users if user['id'] == idUser][0]

        user_list = {
            'id': user_by_id['id'],
            'name': user_by_id['name'],
            'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if
                        theme['id'] in [expert[2] for expert in experts if expert[1] == user_by_id['id']]],
            'interests': [{'id': theme['id'], 'name': theme['name']} for theme in themes if
                          theme['id'] in [interested[2] for interested in interesteds if
                                          interested[1] == user_by_id['id']]]}
        return jsonify(user_list)
    except Exception as e:
        print(e)
        return jsonify({'message': 'Failed get user'})

def check_unique(users_by_expert):
    list_of_unique_users = []
    for i in range(len(users_by_expert)):
        if i == 0: list_of_unique_users.append(users_by_expert[i])
        elif users_by_expert[i] in list_of_unique_users:
            continue
        else: list_of_unique_users.append(users_by_expert[i])
    return list_of_unique_users

def check_unique_id(users_by_expert):
    list_of_unique_id_users = []
    for i in range(len(users_by_expert)):
        for j in range(len(users_by_expert[i])):
            list_of_unique_id_users.append(users_by_expert[i][j]['id'])
    print(users_by_expert)
    return list_of_unique_id_users
@app.route('/get_users_by_interested', methods=['POST'])
def get_users_by_interested():

    try:
        dataJson = request.get_json()
        idThemes = dataJson.get('idTheme', '')
        #print(type(idThemes))
        if idThemes == '':
            return jsonify({'message': 'No idThemes'})

        tables = get_tables()

        experts = tables[0]

        interesteds = tables[1]

        themes = tables[2]

        users = tables[3]

        list_of_users = []
        user_by_expert = [[
            {'id': user['id'],
            'name': user['name'],
            'password': user['password'],
            'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [expert[2] for expert in experts if expert[1] == user['id']]],
            'interests': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [interested[2] for interested in interesteds if interested[1] == user['id']]]}
            for user in users if user['id'] in [expert[1] for expert in experts if expert[2] == idTheme]
        ] for idTheme in idThemes]
        #print(unique_users_id)

        # for i in range(len(user_by_expert)):
        #     for j in range(len(user_by_expert[i])):
        #         list_of_users.append(user_by_expert[i][j])
        # #print(list_of_users)
        # unique_users = check_unique(list_of_users)
        unique_users_id = [check_unique_id(user_by_expert)]
        #print(dir(unique_users_id))
        # a = [[12, 0, 6], [12, 12, 5], [20, 30, 0]]
        unique_users_id_dict = {}
        for r in Counter(x for y in unique_users_id for x in y).items():

            unique_users_id_dict[r[0]] = r[1]
        #print(unique_users_id_dict)

        unique_users_id_dict_sorted = dict(sorted(unique_users_id_dict.items(), key=lambda x: x[1], reverse=True))
        #print("new dict =", unique_users_id_dict_sorted)
        unique_users_id_list_sorted = list(unique_users_id_dict_sorted.keys())
        print(unique_users_id_list_sorted)

        # unique_users = []
        # for uniqueId in unique_users_id_list_sorted:
        #     for i in range(len(user_by_expert)):
        #         for j in range(len(user_by_expert[i])):
        #             if user_by_expert[i][j]['id'] == uniqueId:
        #                 unique_users.append(user_by_expert[i][j])
        # print(unique_users_id_list_sorted)

        unique_users = [[{
            'id': user['id'],
            'name': user['name'],
            'password': user['password'],
            'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [expert[2] for expert in experts if expert[1] == user['id']]],
            'interests': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [interested[2] for interested in interesteds if interested[1] == user['id']]]}
            for user in users if user['id'] == unique_user_id_list_sorted] for unique_user_id_list_sorted in unique_users_id_list_sorted]

        #print(user_by_expert)
        #print(unique_users)

        return jsonify(unique_users)

        #return jsonify(user_by_expert)
    except Exception as e:
        print(e)
        return jsonify({'message': 'Failed get user'})

@app.route('/')
def index():
    return "<h1>Hello, World!</h1>"

# DEBUG MODE:
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)


# print("Таблица создана и заполнена данными.")