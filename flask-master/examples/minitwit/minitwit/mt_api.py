import minitwit
import time
from flask import Flask, request, jsonify, g, json, abort, Response
from flask_basicauth import BasicAuth

app = Flask(__name__)

# default authenticated configuration
app.config['BASIC_AUTH_USERNAME'] = 'thomas'
app.config['BASIC_AUTH_PASSWORD'] = 'me123'

basic_auth = BasicAuth(app)


'''return username of an user_id'''
def get_username(user_id):
    cur = minitwit.query_db('select username from user where user_id = ?', [user_id], one = True)
    return cur[0] if cur else None


def get_credentials(username):
    user_name = minitwit.query_db('''select username from user where user.username = ?''', [username], one=True)
    pw_hash = minitwit.query_db('''select pw_hash from user where user.username = ?''', [username], one=True)
    app.config['BASIC_AUTH_USERNAME'] = user_name[0]
    app.config['BASIC_AUTH_PASSWORD'] = pw_hash[0]


def make_error(status_code, message, reason):
    response = jsonify({
        "status" : status_code,
        "message" : message,
        "reason" : reason
    })
    return response


def populate_db():
    """Re-populates the database with test data"""
    db = minitwit.get_db()
    with app.open_resource('population.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('populatedb')
def populatedb_command():
    """Inputs data in database tables."""
    populate_db()
    print('Database population is completed.')


@app.before_request
def only_json():
    if not request.is_json:
        return make_error(400, "Bad Request", "The browser (or proxy) sent a request that this server could not understand.")


@app.after_request
def after_request(response):
    print response.get_data()
    print response.status
    print response.status_code
    print response.headers
    if response.status_code == 400:
        return make_error(400, "Bad Request", "The browser (or proxy) sent a request that this server could not understand.")
    if response.status_code == 500:
        return make_error(500, "Internal Server Error", "The server encountered an internal error and was unable to complete your request.  Either the server is overloaded or there is an error in the application.")


@app.route('/users/<user_id>/timeline')
def user_timeline(user_id):
    messages = minitwit.query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id and (
            user.user_id = ? or
            user.user_id in (select whom_id from follower
                                    where who_id = ?))
        order by message.pub_date desc limit ?''',
        [user_id, user_id, minitwit.PER_PAGE])
    print messages
    messages = map(dict, messages)
    print messages
    return jsonify(messages)


@app.route('/users/<username>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_info(username):
    """Gets user's information"""
    data = request.get_json()
    get_credentials(username)
    if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    if request.method == 'GET':
        user = minitwit.query_db('''select * from user where user.username = ?''', [username])
        print user
        user = map(dict, user)
        return jsonify(user)
    return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')


@app.route('/users/<username>/add_message', methods=['POST', 'GET', 'PUT', 'DELETE'])
def insert_message(username):
    """Inserts a new message from current <username>"""
    if request.method == 'POST':
        data = request.get_json()
        user_id = minitwit.get_user_id(username)
        get_credentials(username)
        if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
            return make_error(401, 'Unauthorized', 'Correct username and password are required.')
        if data:
            db = minitwit.get_db()
            db.execute('''insert into message (author_id, text, pub_date)
            values (?, ?, ?)''', [user_id, data["text"], int(time.time())])
            db.commit()
        return jsonify(data)
    return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')


@app.route('/users/<username>/messages', methods=['GET', 'POST', 'PUT', 'DELETE'])
def get_user_messages(username):
    """Displays a user's tweets"""
    profile_user = minitwit.query_db('select * from user where username = ?',[username], one=True)
    if profile_user is None:
        return make_error(404, 'Not Found', 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.')
    data = request.get_json()
    get_credentials(username)
    if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    if request.method == 'GET':
        messages = minitwit.query_db('''select message.*, user.* from message, user where user.user_id = message.author_id and user.user_id = ? order by message.pub_date desc limit ?''',
        [profile_user['user_id'], minitwit.PER_PAGE])
        messages = map(dict, messages)
        return jsonify(messages)
    return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')


@app.route('/users/<username1>/follow/<username2>', methods=['POST', 'GET', 'PUT', 'DELETE'])
def add_follow_user(username1, username2):
    """Adds the username1 as follower of the given username2."""
    data = request.get_json()
    get_credentials(username1)
    if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    who_id = minitwit.get_user_id(username1)
    whom_id = minitwit.get_user_id(username2)
    if whom_id is None:
        return make_error(404, 'Not Found', 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.')
    cur = minitwit.query_db('select count(*) from follower where who_id = ? and whom_id = ?', [who_id, whom_id], one=True)
    if cur[0] > 0:
        return make_error(400, "Bad Request", "Data duplicated")
    if request.method == 'POST':
        db = minitwit.get_db()
        db.execute('insert into follower (who_id, whom_id) values (?, ?)', [who_id, whom_id])
        db.commit()
        return jsonify(data)
    return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')


@app.route('/messages', methods=['POST', 'GET', 'PUT', 'DELETE'])
def get_messages():
    '''return all messages from all users '''
    if request.method != 'GET':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')

    messages = minitwit.query_db('''
            select message.text, user.username from message, user
            where message.author_id = user.user_id
            order by message.pub_date desc''',
            )
    print messages
    messages = map(dict, messages)
    print messages
    return jsonify(messages)


@app.route('/messages/<user_id>', methods =['POST', 'GET', 'PUT', 'DELETE'])
def get_message_user(user_id):
    '''return all messages form the user <user_id>'''
    if request.method != 'GET':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')

    messages = minitwit.query_db('''
        select message.text, user.username from message, user
        where message.author_id = user.user_id and user.user_id = ? ''',
        [user_id])
    print messages
    messages = map(dict, messages)

    return jsonify(messages)


@app.route('/users/<user_id>/followers', methods = ['POST', 'GET', 'PUT', 'DELETE'])
def user_followers(user_id):
    '''return all users that are followers of the user <user_id>'''
    if request.method != 'GET':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')

    messages = minitwit.query_db('''
        select u1.username as followee, u2.username as follower from user u1, follower f, user u2
        where u1.user_id = f.who_id and u2.user_id = f.whom_id and u1.user_id = ? ''',
        [user_id])
    print messages
    messages = map(dict, messages)

    return jsonify(messages)


@app.route('/users/<user_id>/follow', methods = ['POST', 'GET', 'PUT', 'DELETE'])
def user_follow(user_id):
    '''return all users that the user <user_id> is following'''
    if request.method != 'GET':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')

    messages = minitwit.query_db('''
        select u1.username as followee, u2.username as follower from user u1, follower f, user u2
        where u1.user_id = f.who_id and u2.user_id = f.whom_id and u1.user_id = ? ''',
        [user_id])

    messages = map(dict, messages)
    print messages
    return jsonify(messages)


@app.route('/messages/<user_id>/add_message', methods=['POST', 'GET', 'PUT', 'DELETE'])
def add_message(user_id):
    '''Insert a message into table message: json data: author_id, text'''
    if not request.json:
        return make_error(400, "Bad Request", "The browser (or proxy) sent a request that this server could not understand.")
    if request.method != 'POST':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')

    data = request.json

    if data:
        username = get_username(user_id)
        get_credentials(username)
        if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
            return make_error(401, 'Unauthorized', 'Invalid Username ad/or Password')

        db = minitwit.get_db()
        db.execute('''insert into message (author_id, text)
        values (?, ?)''',
        [data["author_id"], data["text"]])
        db.commit()
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
