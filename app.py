import sqlite3
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import secrets
from collections import Counter

app = Flask(__name__)
CORS(app)
logging.basicConfig(level = logging.DEBUG)

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
    cursor.execute("SELECT * FROM rating_table")
    rating_table = cursor.fetchall()
    cursor.execute("SELECT * FROM tokens")
    tokens = cursor.fetchall()

    cursor.close()
    conn.close()
    return [experts, interesteds, themes, users, rating_table, tokens]

def add_user(username, password, gmail, contacts, rating):
    with get_connect() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, password, gmail, contacts, rating) VALUES (?, ?, ?, ?, ?)', (username, password, gmail, contacts, rating))
        conn.commit()

@app.route('/api/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users WHERE id = ?", (user_id,))
    cursor.execute("DELETE FROM user_expert_themes WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM user_interested_themes WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM rating_table WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM tokens WHERE user_id = ?", (user_id,))
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

# @app.route('/get_users', methods=['GET'])
# def get_users_route():
#     conn = get_connect()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM user_expert_themes")
#     experts = cursor.fetchall()
#     cursor.execute("SELECT * FROM user_interested_themes")
#     interesteds = cursor.fetchall()
#     cursor.execute("SELECT * FROM themes")
#     themes = cursor.fetchall()
#     cursor.execute("SELECT * FROM Users")
#     users = cursor.fetchall()
#
#     users_list = [{
#         'id': user['id'],
#         'name': user['name'],
#         'password': user['password'],
#         'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [expert[2] for expert in experts if expert[1] == user['id']]],
#         'interests': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [interested[2] for interested in interesteds if interested[1] == user['id']]]}
#         for user in users]
#     cursor.close()
#     conn.close()
#     return jsonify(users_list)

@app.route('/get_themes', methods=['GET'])
def get_themes_route():
    tables = get_tables()
    themes = tables[2]
    themes_list = [{'id': theme['id'], 'name': theme['name']} for theme in themes]
    return jsonify(themes_list)

def create_tocken(tocken, authoriz_user_id):
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO tokens (token, user_id) VALUES (?, ?)''', (tocken, authoriz_user_id))
    conn.commit()
    conn.close()

def delete_tocken(tocken):
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM tokens WHERE token = ?''', (tocken,))
    conn.commit()
    conn.close()
@app.route('/delete-token', methods=['POST'])
def delete_token():
    data = request.get_json()
    tocken = data.get('tocken', '')
    try:
        delete_tocken(tocken)
        return jsonify({'message': 'Token deleted'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Cant delete token'})

@app.route('/api/registration', methods=['POST'])
def registration():
    dataJson = request.get_json()
    data = dataJson.get('data', '')
    username = data.get('name', '')
    password = data.get('password', '')
    gmail = data.get('gmail', '')
    contacts = data.get('contacts', '')
    rating = 0
    try:
        add_user(username, password, gmail, contacts, rating)

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
            'contacts': last_user['contacts'],
            'rating': last_user['rating'],
            'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [expert[2] for expert in experts if expert[1] == last_user['id']]],
            'interests': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [interested[2] for interested in interesteds if interested[1] == last_user['id']]]}

        tocken = secrets.token_urlsafe()
        create_tocken(tocken, last_user['id'])
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
    #print(name)
    try:
        add_theme(name)
        tables = get_tables()
        themes = tables[2]

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
    contacts = data.get('contacts', '')
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

            change_column(contacts, user_id)

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
            'gmail': authoriz_user['gmail'],
            'contacts': authoriz_user['contacts'],
            'rating': authoriz_user['rating'],
            'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if
                        theme['id'] in [expert[2] for expert in experts if expert[1] == authoriz_user['id']]],
            'interests': [{'id': theme['id'], 'name': theme['name']} for theme in themes if
                          theme['id'] in [interested[2] for interested in interesteds if interested[1] == authoriz_user['id']]]}

        tocken = secrets.token_urlsafe()
        create_tocken(tocken, authoriz_user['id'])
        return jsonify({'data': user_list, 'tocken': tocken})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Failed autorization'})

@app.route('/read_token', methods=['POST'])
def read_token():
    try:
        data = request.get_json()
        tocken = data.get('tocken', '')

        tables = get_tables()
        experts = tables[0]
        interesteds = tables[1]
        themes = tables[2]
        users = tables[3]
        tokens = tables[5]

        token_user = [[user for user in users if user['id'] == idUser] for idUser in [token[2] for token in tokens if token[1] == tocken]][0][0]
        user_list = {
            'id': token_user['id'],
            'name': token_user['name'],
            'password': token_user['password'],
            'gmail': token_user['gmail'],
            'contacts': token_user['contacts'],
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
            'contacts': user_by_id['contacts'],
            'rating': user_by_id['rating'],
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
    return list_of_unique_id_users
@app.route('/get_users_by_interested', methods=['POST'])
def get_users_by_interested():

    try:
        dataJson = request.get_json()
        idThemes = dataJson.get('idTheme', '')
        if idThemes == '':
            return jsonify({'message': 'No idThemes'})

        tables = get_tables()
        experts = tables[0]
        interesteds = tables[1]
        themes = tables[2]
        users = tables[3]

        user_by_expert = [[
            {'id': user['id'],
            'name': user['name'],
            #'password': user['password'],
            'contacts': user['contacts'],
            'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [expert[2] for expert in experts if expert[1] == user['id']]],
            'interests': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [interested[2] for interested in interesteds if interested[1] == user['id']]]}
            for user in users if user['id'] in [expert[1] for expert in experts if expert[2] == idTheme]
        ] for idTheme in idThemes]
        unique_users_id = [check_unique_id(user_by_expert)]
        unique_users_id_dict = {}
        for r in Counter(x for y in unique_users_id for x in y).items():
            unique_users_id_dict[r[0]] = r[1]
        unique_users_id_dict_sorted = dict(sorted(unique_users_id_dict.items(), key=lambda x: x[1], reverse=True))
        unique_users_id_list_sorted = list(unique_users_id_dict_sorted.keys())
        unique_users = [[{
            'id': user['id'],
            'name': user['name'],
            'contacts': user['contacts'],
            'rating': user['rating'],
            'experts': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [expert[2] for expert in experts if expert[1] == user['id']]],
            'interests': [{'id': theme['id'], 'name': theme['name']} for theme in themes if theme['id'] in [interested[2] for interested in interesteds if interested[1] == user['id']]]}
            for user in users if user['id'] == unique_user_id_list_sorted] for unique_user_id_list_sorted in unique_users_id_list_sorted]
        return jsonify(unique_users)
    except Exception as e:
        print(e)
        return jsonify({'message': 'Failed get user'})

def change_column(contacts, idUser):
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET contacts = ? WHERE id = ?''', (contacts, idUser))
    conn.commit()
    conn.close()

@app.route('/change-contacts', methods=['POST'])
def change_contacts():
    data = request.get_json()
    idUser = data.get('id', '')
    contacts = data.get('contacts', '')
    try:
        change_column(contacts, idUser)
        return jsonify({'message': 'Changed succesfully'})
    except Exception as e:
        print(e)
        return jsonify({'message': "Don't change"})

def give_rating(rating, idUserRating, idUserRated):
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO rating_table (idUserRating, idUserRated, rating) VALUES (?, ?, ?)''', ( idUserRating, idUserRated, rating))
    conn.commit()
    conn.close()

def change_rating(rating, idUser):
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET rating = ? WHERE id = ?''', (rating, idUser))
    conn.commit()
    conn.close()


@app.route('/give-rating', methods=['POST'])
def give_rating_route():
    dataJson = request.get_json()
    data = dataJson.get('data', '')
    #print(data)
    idUserRating = data.get('idUserRating', '')
    idUserRated = data.get('idUserRated', '')
    rating = data.get('rating', '')
    #print(rating)
    try:
        tables = get_tables()

        table_rating = tables[4]

        if (idUserRating in [table_rating_elem['idUserRating'] for table_rating_elem in
                             table_rating] and idUserRated in [table_rating_elem['idUserRated'] for table_rating_elem in
                                                               table_rating]):
            return jsonify({'message': "You alredy rated"})

        give_rating(rating, idUserRating, idUserRated)

        tables = get_tables()

        table_rating = tables[4]

        #print([table_rating_elem['rating'] for table_rating_elem in table_rating if table_rating_elem['idUserRated'] == idUserRated])
        #print(len([table_rating_elem['rating'] for table_rating_elem in table_rating if table_rating_elem['idUserRated'] == idUserRated]))
        #print(sum([table_rating_elem['rating'] for table_rating_elem in table_rating if table_rating_elem['idUserRated'] == idUserRated]))
        rating_final = sum([table_rating_elem['rating'] for table_rating_elem in table_rating if table_rating_elem['idUserRated'] == idUserRated]) / len([table_rating_elem['rating'] for table_rating_elem in table_rating if table_rating_elem['idUserRated'] == idUserRated])
        #print(rating_final)
        change_rating(round(rating_final, 1), idUserRated)

        return jsonify({'message': 'Changed succesfully'})
    except Exception as e:
        print(e)
        return jsonify({'message': "Don't change"})

@app.route('/')
def index():
    return "<h1>Hello, World!</h1>"

#DEBUG MODE:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


# print("Таблица создана и заполнена данными.")