import minitwit
import os
import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, jsonify, g, json, abort, Response, flash, _app_ctx_stack, session
from flask_basicauth import BasicAuth
from werkzeug import check_password_hash, generate_password_hash

app = Flask(__name__)

# configuration
# DATABASE = '/tmp/minitwit.db'
# DATABASE = '/tmp/mt_api.db'
DATABASE = os.path.join(app.root_path, 'mt_api.db')
PER_PAGE = 30
DEBUG = True
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
# SECRET_KEY = '\x01\xeei\xa6\xa7\x7f\xec\xd0\xfb\x83fv|\xf0*\xe7\xa9R\x8b\xca0\x12\x03\xfc'

# create our little application :)
app = Flask('mt_api')
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)

# default authenticated configuration
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'admin123'

basic_auth = BasicAuth(app)


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = query_db('select user_id from user where username = ?',
                  [username], one=True)
    return rv[0] if rv else None


# @app.before_request
# def before_request():
#     g.user = None
#     if 'user_id' in session:
#         g.user = query_db('select * from user where user_id = ?',
#                           [session['user_id']], one=True)


def get_username(user_id):
    '''return username of an user_id'''
    cur = query_db('select username from user where user_id = ?', [user_id], one = True)
    return cur[0] if cur else None


def get_credentials(username):
    user_name = query_db('''select username from user where user.username = ?''', [username], one=True)
    pw_hash = query_db('''select pw_hash from user where user.username = ?''', [username], one=True)
    app.config['BASIC_AUTH_USERNAME'] = user_name[0]
    app.config['BASIC_AUTH_PASSWORD'] = pw_hash[0]


def get_credentials_by_user_id(user_id):
    user_name = query_db('''select username from user where user.user_id = ?''', [user_id], one=True)
    pw_hash = query_db('''select pw_hash from user where user.user_id = ?''', [user_id], one=True)
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
    db = get_db()
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
        # get_credentials(data["username"])
        # if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        #     return make_error(401, 'Unauthorized', 'Correct username and password are required.')
        if request.method == 'GET':
            user = query_db('''select * from user where user.username = ?''', [data['username']], one=True)
            print user
            # user = map(dict, user)
            if user:
                user = dict(user)
                return jsonify(user)
            return jsonify(user)
    if 'user_id' in data:
        # get_credentials_by_user_id(data["user_id"])
        # if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        #     return make_error(401, 'Unauthorized', 'Correct username and password are required.')
        if request.method == 'GET':
            user = query_db('''select * from user where user_id = ?''', [data['user_id']], one=True)
            if user:
                user = dict(user)
                return jsonify(user)
            return jsonify(user)
            # user = map(dict, user)
            # user = dict(user)
            # return jsonify(user)
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
            db = get_db()
            db.execute('''insert into message (author_id, text, pub_date)
            values (?, ?, ?)''', [user_id, data["text"], int(time.time())])
            db.commit()
            print 'Your message was recorded'
        return jsonify(data)
    return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')


@app.route('/users/<username>/messages', methods=['GET', 'POST', 'PUT', 'DELETE'])
def get_user_messages(username):
    """Displays a user's tweets"""
    profile_user = query_db('select * from user where username = ?',[username], one=True)
    if profile_user is None:
        return make_error(404, 'Not Found', 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.')
    data = request.get_json()
    get_credentials(data["username"])
    if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    if request.method == 'GET':
        messages = query_db('''select message.*, user.* from message, user where user.user_id = message.author_id and user.user_id = ? order by message.pub_date desc limit ?''',
        [profile_user['user_id'], PER_PAGE])
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
    who_id = get_user_id(username1)
    whom_id = get_user_id(username2)
    if whom_id is None:
        return make_error(404, 'Not Found', 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.')
    cur = query_db('select count(*) from follower where who_id = ? and whom_id = ?', [who_id, whom_id], one=True)
    if cur[0] > 0:
        return make_error(422, "Unprocessable Entity", "Data duplicated")
    if request.method == 'POST':
        db = get_db()
        db.execute('insert into follower (who_id, whom_id) values (?, ?)', [who_id, whom_id])
        db.commit()
        print 'You are now following %s' % username2
        return jsonify(data)
    return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')


@app.route('/messages', methods=['POST', 'GET', 'PUT', 'DELETE'])
def get_messages():
    '''return all messages from all users '''
    if request.method != 'GET':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')

    messages = query_db('''
            select message.*, user.* from message, user
            where message.author_id = user.user_id
            order by message.pub_date desc limit?''', [PER_PAGE])
    messages = map(dict, messages)
    return jsonify(messages)


@app.route('/messages/<user_id>', methods =['POST', 'GET', 'PUT', 'DELETE'])
def get_message_user(user_id):
    '''return all messages form the user <user_id>'''
    if request.method != 'GET':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')
    data = request.json
    messages = query_db('''
        select message.text, user.username from message, user
        where message.author_id = user.user_id and user.user_id = ? ''',
        [user_id])
    messages = map(dict, messages)

    return jsonify(messages)


@app.route('/users/<user_id>/followers', methods = ['POST', 'GET', 'PUT', 'DELETE'])
def user_followers(user_id):
    '''return all users that are followers of the user <user_id>'''
    if request.method != 'GET':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')
    data = request.json
    get_credentials_by_user_id(user_id)
    if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    messages = query_db('''
        select u1.username as followee, u2.username as follower from user u1, follower f, user u2
        where u1.user_id = f.who_id and u2.user_id = f.whom_id and u1.user_id = ? ''',
        [user_id])
    messages = map(dict, messages)

    return jsonify(messages)


@app.route('/users/<user_id>/follow', methods = ['POST', 'GET', 'PUT', 'DELETE'])
def user_follow(user_id):
    # '''return all users that the user <user_id> is following'''
    '''return 1 if user_id has followers. Otherwise, return None'''
    if request.method != 'GET':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')
    data = request.json
    get_credentials_by_user_id(user_id)
    if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    # messages = query_db('''
    #     select u1.username as followee, u2.username as follower from user u1, follower f, user u2
    #     where u1.user_id = f.who_id and u2.user_id = f.whom_id and u1.user_id = ? ''',
    #     [user_id])
    messages = query_db('''
                        select 1 from follower
                        where follower.who_id = ? and follower.whom_id = ?''', [data['user_id'], data['profile_user_id']], one=True)
    print messages
    # messages = map(dict, messages[0])
    if messages:
        return jsonify(messages[0])
    else:
        return jsonify(messages)


@app.route('/messages/<user_id>/add_message', methods=['POST', 'GET', 'PUT', 'DELETE'])
def add_message(user_id):
    '''Insert a message into table message: json data: author_id, text'''
    if not request.json:
        return make_error(400, "Bad Request", "The browser (or proxy) sent a request that this server could not understand.")
    if request.method != 'POST':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')

    data = request.json
    get_credentials_by_user_id(user_id)
    if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    if data:
        username = get_username(user_id)
        get_credentials(username)
        if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
            return make_error(401, 'Unauthorized', 'Invalid Username ad/or Password')

        db = get_db()
        db.execute('''insert into message (author_id, text)
        values (?, ?)''',
        [data["author_id"], data["text"]])
        db.commit()
        print 'Your message was successfully recorded'
    return jsonify(data)


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
        '''Check duplicate'''
        cur = query_db('select count(*) from follower where who_id = ? and whom_id = ?', [user_id, data["whom_id"]], one=True)
        if cur[0] > 0:
            return make_error(422, "Unprocessable Entity", "Data duplicated")
        db = get_db()
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
        '''Check who_id and whom_id existing'''
        cur = query_db('select count(*) from follower where who_id = ? and whom_id = ?', [user_id, data["whom_id"]], one=True)
        if cur[0] == 0:
            return make_error(404, 'Not Found', 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.')
        db = get_db()
        db.execute('''delete from follower
        where who_id = ? and whom_id = ?''',
         [user_id, data["whom_id"]])
        db.commit()
        print 'You are no longer following user has ', data["whom_id"]
    return jsonify(data)


@app.route('/users/<user_id>/change_password', methods = ['POST', 'GET', 'PUT', 'DELETE'])
def change_password(user_id):
    '''Change password: json data: password, confirmed_password'''
    if not request.json:
        return make_error(400, "Bad Request", "The browser (or proxy) sent a request that this server could not understand.")
    if request.method != 'PUT':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')

    data = request.json
    get_credentials_by_user_id(user_id)
    if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    if data:
        '''Check user_id existing'''
        cur = query_db('select count(*) from user where user_id = ?', [user_id], one=True)
        if cur[0] == 0:
            return make_error(404, 'Not Found', 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.')
        '''check password and confirmed password are equal'''
        if data["password"] != data["confirmed_password"]:
            return make_error(422, "Unprocessable Entity", "password and confirmed password not consistent")
        db = get_db()
        pw = generate_password_hash(data['password'])
        db.execute('''update user
        set pw_hash = ?
        where user_id = ?''',
        [pw, user_id])
        db.commit()
        print 'Your password was successfully changed'
    return jsonify(data)


@app.route('/users/<user_id>/change_email', methods = ['POST', 'GET', 'PUT', 'DELETE'])
def change_email(user_id):
    '''Change email: json data: email, confirmed_email'''
    if not request.json:
        return make_error(400, "Bad Request", "The browser (or proxy) sent a request that this server could not understand.")
    if request.method != 'PUT':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')

    data = request.json
    get_credentials_by_user_id(user_id)
    if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    if data:
        '''Check user_id existing'''
        cur = query_db('select count(*) from user where user_id = ?', [user_id], one=True)
        if cur[0] == 0:
            return make_error(404, 'Not Found', 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.')
        '''check password and confirmed password are equal'''
        if data["email"] != data["confirmed_email"]:
            return make_error(422, "Unprocessable Entity", "password and confirmed password not consistent")
        db = get_db()
        email = data["email"]
        db.execute('''update user
        set email = ?
        where user_id = ?''',
        [email, user_id])
        db.commit()
        print 'Your email was successfully changed'
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
        # if not data["username"] or not data["email"] or not data["password"] \
        #     or not data["confirmed_password"] or data["password"] != data["confirmed_password"]:
        #     return make_error(400, "Bad Request", "The browser (or proxy) sent a request that this server could not understand.")
        # '''check duplicate'''
        # cur = query_db('select count(*) from user where username = ?', [data["username"]], one=True)
        # cur1 = query_db('select count(*) from user where email = ?', [data["email"]], one=True)
        # if cur[0] > 0:
        #     return make_error(422, "Unprocessable Entity", "Duplicated Username")
        # if cur1[0] > 0:
        #     return make_error(422, "Unprocessable Entity", "Duplicated email")
        # pw = generate_password_hash(data["password"])
        db = get_db()
        db.execute('''insert into user (username, email, pw_hash)
            values (?, ?, ?)''',
            [data["username"], data["email"], data["pw_hash"]])
        db.commit()
        print 'You were successfully registered'
    return jsonify(data)


@app.route('/users', methods = ['POST', 'GET', 'PUT', 'DELETE'])
def user_time_line():
    '''get user timeline or if no user is logged in it will get the public timeline instead.
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
    user = query_db('''select message.*, user.* from message, user
    where message.author_id = user.user_id and (
        user.user_id = ? or
        user.user_id in (select whom_id from follower
                                where who_id = ?))
    order by message.pub_date desc limit ?''', [data['user_id'], data['user_id'], PER_PAGE])
    print '\nbreak1\n'
    print user
    # print user[0]['username']
    user = map(dict, user)
    print '\nbreak2\n'
    print user
    return jsonify(user)


@app.route('/timeline', methods=['POST', 'GET', 'PUT', 'DELETE'])
def public_time_line():
    '''display latest messages of all users.'''
    # if not request.json:
    #     return make_error(400, "Bad Request", "The browser (or proxy) sent a request that this server could not understand.")
    # if request.method != 'GET':
    #     return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')
    #     data = request.get_json();
    messages=query_db('''select message.*, user.* from message, user where message.author_id = user.user_id order by message.pub_date desc limit ?''', [PER_PAGE])
    messages = map(dict, messages)
    return jsonify(messages)


if __name__ == '__main__':
    app.run(debug=True)
