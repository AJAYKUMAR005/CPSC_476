import minitwit
import os
import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, jsonify, g, json, abort, Response, flash, _app_ctx_stack, session
from flask_basicauth import BasicAuth
from werkzeug import check_password_hash, generate_password_hash
import uuid

app = Flask(__name__)

# configuration
# DATABASE = '/tmp/minitwit.db'
# DATABASE = os.path.join(app.root_path, 'mt_api.db')
DATABASE0 = os.path.join(app.root_path, 'mt_api0.db')
DATABASE1 = os.path.join(app.root_path, 'mt_api1.db')
DATABASE2 = os.path.join(app.root_path, 'mt_api2.db')
PER_PAGE = 30
DEBUG = True
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

# create our little application :)
app = Flask('mt_api')
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)

# default authenticated configuration
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'admin123'

basic_auth = BasicAuth(app)

def get_db(server_id):
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    DATABASE = "DATABASE" + str(server_id)

    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db0') and server_id == 0:
        top.sqlite_db0 = sqlite3.connect(app.config[DATABASE], detect_types=sqlite3.PARSE_DECLTYPES)
        top.sqlite_db0.row_factory = sqlite3.Row
    if not hasattr(top, 'sqlite_db1') and server_id == 1:
        top.sqlite_db1 = sqlite3.connect(app.config[DATABASE], detect_types=sqlite3.PARSE_DECLTYPES)
        top.sqlite_db1.row_factory = sqlite3.Row
    if not hasattr(top, 'sqlite_db2') and server_id == 2:
        top.sqlite_db2 = sqlite3.connect(app.config[DATABASE], detect_types=sqlite3.PARSE_DECLTYPES)
        top.sqlite_db2.row_factory = sqlite3.Row

    if server_id == 0:
        return top.sqlite_db0
    elif server_id == 1:
        return top.sqlite_db1
    else:
        return top.sqlite_db2


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db0'):
        top.sqlite_db0.close()
    if hasattr(top, 'sqlite_db1'):
        top.sqlite_db1.close()
    if hasattr(top, 'sqlite_db2'):
        top.sqlite_db2.close()


def init_db():
    """Initializes the database."""
    sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
    sqlite3.register_adapter(uuid.UUID, lambda u: buffer(u.bytes_le))
    for i in range(0,3):
        db = get_db(i)
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def query_db(server_id, query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db(server_id).execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = query_db(0, 'select user_id from user where username = ?',
                  [username], one=True)
    if rv:
        return rv[0]

    rv = query_db(1, 'select user_id from user where username = ?',
                  [username], one=True)
    if rv:
        return rv[0]

    rv = query_db(2, 'select user_id from user where username = ?',
                  [username], one=True)
    if rv:
        return rv[0]
    return None


def get_username(user_id):
    '''return username of an user_id'''
    server_id = get_server_id(user_id)
    cur = query_db(server_id, 'select username from user where user_id = ?', [user_id], one = True)
    return cur[0] if cur else None


def get_server_id(user_id):
    '''return sharding for server'''
    return (uuid.UUID(user_id).int) % 3


def get_credentials(username):
    user_id = get_user_id(username)
    server_id = get_server_id(user_id)
    user_name = query_db(server_id, '''select username from user where user.username = ?''', [username], one=True)
    pw_hash = query_db(server_id, '''select pw_hash from user where user.username = ?''', [username], one=True)
    app.config['BASIC_AUTH_USERNAME'] = user_name[0]
    app.config['BASIC_AUTH_PASSWORD'] = pw_hash[0]


def get_credentials_by_user_id(user_id):
    server_id = get_server_id(user_id)
    user_name = query_db(server_id, '''select username from user where user.user_id = ?''', [user_id], one=True)
    pw_hash = query_db(server_id, '''select pw_hash from user where user.user_id = ?''', [user_id], one=True)
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
    for i in range(0,3):
        population = 'population' + str(i) + '.sql'
        db = get_db(i)
        with app.open_resource(population, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.cli.command('populatedb')
def populatedb_command():
    """Inputs data in database tables."""
    populate_db()
    print('Database population is completed.')


@app.after_request
def after_request(response):
    if response.status_code == 400:
        return make_error(400, "Bad Request", "The browser (or proxy) sent a request that this server could not understand.")
    if response.status_code == 500:
        return make_error(500, "Internal Server Error", "The server encountered an internal error and was unable to complete your request.  Either the server is overloaded or there is an error in the application.")
    if response.status_code == 404:
        return make_error(404, 'Not Found', 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.')
    if response.status_code == 405:
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')
    return response


@app.route('/users/<id_or_name>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_info(id_or_name):
    """Gets user's information"""
    data = request.get_json()
    if 'username' in data:
        user_id = get_user_id(data['username'])
        if user_id:
            print data['username']
            print user_id
            print repr(user_id)
            print type(user_id)
            server_id = get_server_id(str(user_id))
            if request.method == 'GET':
                user = query_db(server_id, '''select * from user where user.username = ?''', [data['username']], one=True)
                if user:
                    user = dict(user)
                    return jsonify(user)
                return jsonify(user)
        else:
            return jsonify(None)
    if 'user_id' in data:
        server_id = get_server_id(data['user_id'])
        if request.method == 'GET':
            user = query_db(server_id, '''select * from user where user_id = ?''', [data['user_id']], one=True)
            if user:
                user = dict(user)
                return jsonify(user)
            return jsonify(user)
    return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')


@app.route('/users/<username>/add_message', methods=['POST', 'GET', 'PUT', 'DELETE'])
def insert_message(username):
    """Inserts a new message from current <username>"""
    if request.method == 'POST':
        data = request.get_json()
        user_id = get_user_id(username)
        get_credentials(data["username"])
        if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
            return make_error(401, 'Unauthorized', 'Correct username and password are required.')
        if data:
            server_id = get_server_id(user_id)
            db = get_db(server_id)
            db.execute('''insert into message (author_id, text, pub_date)
            values (?, ?, ?)''', [user_id, data["text"], int(time.time())])
            db.commit()
            print 'Your message was recorded'
        return jsonify(data)
    return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')


@app.route('/users/<username>/messages', methods=['GET', 'POST', 'PUT', 'DELETE'])
def get_user_messages(username):
    """Displays a user's tweets"""
    user_id = get_user_id(username)
    server_id = get_server_id(user_id)
    profile_user = query_db(server_id, 'select * from user where username = ?',[username], one=True)
    if profile_user is None:
        return make_error(404, 'Not Found', 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.')
    data = request.get_json()
    if request.method == 'GET':
        messages = query_db(server_id,'''select message.*, user.* from message, user where user.user_id = message.author_id and user.user_id = ? order by message.pub_date desc limit ?''',
        [profile_user['user_id'], PER_PAGE])
        messages = map(dict, messages)
        return jsonify(messages)
    return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')


@app.route('/users/<user_id>/follow', methods = ['POST', 'GET', 'PUT', 'DELETE'])
def user_follow(user_id):
    '''return 1 if user_id has followers. Otherwise, return None'''
    if request.method != 'GET':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')
    data = request.json
    get_credentials_by_user_id(user_id)
    if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    server_id = get_server_id(str(user_id))
    messages = query_db(server_id, '''
                        select 1 from follower
                        where follower.who_id = ? and follower.whom_id = ?''', [data['user_id'], data['profile_user_id']], one=True)
    print messages
    if messages:
        return jsonify(messages[0])
    else:
        return jsonify(messages)


@app.route('/users/<user_id>/add_follow', methods = ['POST', 'GET', 'PUT', 'DELETE'])
def add_follow(user_id):
    '''Insert follow: json data: whom_id'''
    if not request.json:
        return make_error(400, "Bad Request", "The browser (or proxy) sent a request that this server could not understand.")
    if request.method != 'POST':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')

    data = request.json
    get_credentials_by_user_id(user_id)
    if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    if data:
        server_id = get_server_id(user_id)
        db = get_db(server_id)
        db.execute('''insert into follower (who_id, whom_id)
            values (?, ?)''',
            [user_id, data["whom_id"]])
        db.commit()
        print 'You are following user has user_id ', data['whom_id']
    return jsonify(data)


@app.route('/users/<user_id>/unfollow', methods = ['POST', 'GET', 'PUT', 'DELETE'])
def remove_follow(user_id):
    '''Unfollow: json data: whom_id'''
    if not request.json:
        return make_error(400, "Bad Request", "The browser (or proxy) sent a request that this server could not understand.")
    if request.method != 'DELETE':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')

    data = request.json
    get_credentials_by_user_id(user_id)
    if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    if data:
        server_id = get_server_id(user_id)
        db = get_db(server_id)
        db.execute('''delete from follower
        where who_id = ? and whom_id = ?''',
         [user_id, data["whom_id"]])
        db.commit()
        print 'You are no longer following user has ', data["whom_id"]
    return jsonify(data)


@app.route('/users/Sign_up', methods = ['POST', 'GET', 'PUT', 'DELETE'])
def Sign_up():
    '''User Sign up: json data: username, email, password, confirmed_password'''
    if not request.json:
        return make_error(400, "Bad Request", "The browser (or proxy) sent a request that this server could not understand.")
    if request.method != 'POST':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')

    data = request.get_json()
    print data
    if data:
        user_id = uuid.uuid4()
        server_id = get_server_id(str(user_id))
        db = get_db(server_id)
        db.execute('''insert into user values (?, ?, ?, ?)''',
            [str(user_id), data["username"], data["email"], data["pw_hash"]])
        db.commit()
        print 'You were successfully registered'
    return jsonify(data)


@app.route('/users', methods = ['POST', 'GET', 'PUT', 'DELETE'])
def user_time_line():
    '''get user timeline
    '''
    if not request.json:
        return make_error(400, "Bad Request", "The browser (or proxy) sent a request that this server could not understand.")
    if request.method != 'GET':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')
    data = request.get_json();
    if 'user_id' in data:
        get_credentials_by_user_id(data["user_id"])
        if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
            return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    server_id = get_server_id(data['user_id'])
    user = query_db(server_id, '''select message.*, user.* from message, user where message.author_id = user.user_id and user.user_id = ? order by message.pub_date desc limit ?''', [data['user_id'], PER_PAGE])

    whom_id_set = query_db(server_id, '''select whom_id from follower where who_id = ?''', [data['user_id']])

    for i in whom_id_set:
        print i['whom_id']
        server_id = get_server_id(i['whom_id'])
        print server_id
        follower = query_db(server_id, '''select message.*, user.* from message, user where message.author_id = user.user_id and user.user_id = ? order by message.pub_date desc limit ?''', [i['whom_id'], PER_PAGE])
        user.extend(follower)

    user = map(dict, user)
    return jsonify(user)


@app.route('/timeline', methods=['POST', 'GET', 'PUT', 'DELETE'])
def public_time_line():
    '''display latest messages of all users.'''
    if request.method != 'GET':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')
    messages_server0 = query_db(0, '''select message.*, user.* from message, user where author_id = user.user_id order by message.pub_date desc limit ?''', [PER_PAGE])
    messages_server1 = query_db(1, '''select message.*, user.* from message, user where author_id = user.user_id order by message.pub_date desc limit ?''', [PER_PAGE])
    messages_server2 = query_db(2, '''select message.*, user.* from message, user where author_id = user.user_id order by message.pub_date desc limit ?''', [PER_PAGE])

    messages_server0.extend(messages_server1)
    messages_server0.extend(messages_server2)
    messages = map(dict, messages_server0)
    return jsonify(messages)


if __name__ == '__main__':
    app.run(debug=True)
