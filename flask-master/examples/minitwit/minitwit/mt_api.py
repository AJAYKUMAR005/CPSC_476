import minitwit
import os
import time
import uuid
# from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, jsonify, g, json, abort, Response, flash, _app_ctx_stack, session
from flask_basicauth import BasicAuth
from werkzeug import check_password_hash, generate_password_hash
from flask_cassandra import CassandraCluster
from cassandra.query import dict_factory

app = Flask(__name__)
cassandra = CassandraCluster();
app.config['CASSANDRA_NODES'] = ['127.0.0.1']
CASSANDRA_NODES = '127.0.0.1'

# configuration
# DATABASE = '/tmp/minitwit.db'
# DATABASE = os.path.join(app.root_path, 'mt_api.db')
DATABASE = 'mt_api';
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


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'cassandra_db'):
        top.cassandra_db = cassandra.connect()
        top.cassandra_db.set_keyspace(DATABASE)
        top.cassandra_db.row_factory = dict_factory
    return top.cassandra_db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'cassandra_db'):
        top.cassandra_db.shutdown()


def init_db():
    """Initializes the database."""
    db = cassandra.connect()

    #create database
    db.execute('drop keyspace if exists mt_api')
    db.execute('create keyspace mt_api with replication = { \'class\' : \'SimpleStrategy\', \'replication_factor\': 3}')
    db.execute('USE mt_api')

    #create table
    db.execute('drop table if exists mt_api.user')
    db.execute('create table user (user_id uuid, username text, email text, pw_hash text, primary key (username, user_id))')
    db.execute('drop table if exists mt_api.message')
    db.execute('create table message (user_id uuid, username text, email text, pub_date int, text text, whom_id set<uuid>, who_id set<uuid>, primary key ((username, user_id, email), pub_date)) with clustering order by (pub_date desc)')
    db.execute('drop index if exists mt_api.user_user_id')
    db.execute('create index user_user_id on user(user_id)')
    db.execute('drop index if exists mt_api.message_user_id')
    db.execute('create index message_user_id on message(user_id)')
    db.execute('drop index if exists mt_api.message_username')
    db.execute('create index message_username on message(username)')


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    query = get_db().prepare(query)
    cur = get_db().execute(query, args)
    rv = cur[:]
    return (rv[0] if rv else None) if one else rv


def get_user_id(username):
    """Convenience method to look up the id for a username."""
    print username
    rv = query_db('select user_id from user where username = ?', [username], one=True)
    return rv['user_id'] if rv else None


def get_username(user_id):
    '''return username of an user_id'''
    cur = query_db('select username from user where user_id = ?', [user_id], one = True)
    return cur[0] if cur else None


def get_credentials(username):
    user_name = query_db('''select username from user where username = ?''', [username], one=True)
    pw_hash = query_db('''select pw_hash from user where username = ?''', [username], one=True)
    app.config['BASIC_AUTH_USERNAME'] = user_name['username']
    app.config['BASIC_AUTH_PASSWORD'] = pw_hash['pw_hash']


def get_credentials_by_user_id(user_id):
    user_name = query_db('''select username from mt_api.user where user_id = ?''', [uuid.UUID(user_id)], one=True)
    pw_hash = query_db('''select pw_hash from mt_api.user where user_id = ?''', [uuid.UUID(user_id)], one=True)
    print user_name
    print pw_hash
    app.config['BASIC_AUTH_USERNAME'] = user_name['username']
    app.config['BASIC_AUTH_PASSWORD'] = pw_hash['pw_hash']


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

    #populate user
    db.execute(
        """
        insert into mt_api.user (user_id, username, email, pw_hash) values (%s, %s, %s, %s)
        """,
        (uuid.UUID('{ba4f7e02-a5d1-4c60-9a95-de51142aa51a}'), "thomas", "thomas@gmail.com", "pbkdf2:sha256:50000$r1fUXyrZ$5908841c968862270f5a49550fa46d188680922d2c9c3e571f75fa248034d09d")
    )
    db.execute(
        """
        insert into mt_api.user (user_id, username, email, pw_hash) values (%s, %s, %s, %s)
        """,
        (uuid.UUID('{c405ae0d-b7f1-44dd-8c95-f442fea668ab}'), "bob", "bob@gmail.com", "pbkdf2:sha256:50000$r1fUXyrZ$5908841c968862270f5a49550fa46d188680922d2c9c3e571f75fa248034d09d")
    )
    db.execute(
        """
        insert into mt_api.user (user_id, username, email, pw_hash) values (%s, %s, %s, %s)
        """,
        (uuid.UUID('{cfca912b-eaaa-449f-8162-682289e23e4b}'), "eve", "eve@gmail.com", "pbkdf2:sha256:50000$r1fUXyrZ$5908841c968862270f5a49550fa46d188680922d2c9c3e571f75fa248034d09d")
    )
    db.execute(
        """
        insert into mt_api.user (user_id, username, email, pw_hash) values (%s, %s, %s, %s)
        """,
        (uuid.UUID('{d68a329e-caac-4114-8e0b-e3be895fb538}'), "smith", "smith@gmail.com", "pbkdf2:sha256:50000$r1fUXyrZ$5908841c968862270f5a49550fa46d188680922d2c9c3e571f75fa248034d09d")
    )
    db.execute(
        """
        insert into mt_api.user (user_id, username, email, pw_hash) values (%s, %s, %s, %s)
        """,
        (uuid.UUID('{304c9b29-4126-11e8-ae9a-9cb6d012d2ed}'), "admin", "admin@gmail.com", "pbkdf2:sha256:50000$r1fUXyrZ$5908841c968862270f5a49550fa46d188680922d2c9c3e571f75fa248034d09d")
    )

    #populate message
    db.execute(
        '''
        insert into mt_api.message (user_id, username, email, pub_date, text, whom_id, who_id)
        values (%s, %s, %s, %s, %s, %s, %s)
        ''',
        (uuid.UUID('{ba4f7e02-a5d1-4c60-9a95-de51142aa51a}'), 'thomas', 'thomas@gmail.com', 1518323568, 'hello world', {uuid.UUID('{c405ae0d-b7f1-44dd-8c95-f442fea668ab}'), uuid.UUID('{cfca912b-eaaa-449f-8162-682289e23e4b}')}, {uuid.UUID('{cfca912b-eaaa-449f-8162-682289e23e4b}'), uuid.UUID('{d68a329e-caac-4114-8e0b-e3be895fb538}')})
    )
    db.execute(
        '''
        insert into mt_api.message (user_id, username, email, pub_date, text, whom_id, who_id)
        values (%s, %s, %s, %s, %s, %s, %s)
        ''',
        (uuid.UUID('{ba4f7e02-a5d1-4c60-9a95-de51142aa51a}'), 'thomas', 'thomas@gmail.com', 1518409844, 'testing population', {uuid.UUID('{c405ae0d-b7f1-44dd-8c95-f442fea668ab}'), uuid.UUID('{cfca912b-eaaa-449f-8162-682289e23e4b}')}, {uuid.UUID('{cfca912b-eaaa-449f-8162-682289e23e4b}'), uuid.UUID('{d68a329e-caac-4114-8e0b-e3be895fb538}')})
    )
    db.execute(
        '''
        insert into mt_api.message (user_id, username, email, pub_date, text, whom_id, who_id)
        values (%s, %s, %s, %s, %s, %s, %s)
        ''',
        (uuid.UUID('{c405ae0d-b7f1-44dd-8c95-f442fea668ab}'), 'bob', 'bob@gmail.com', 1518409690, 'hello from bob', {uuid.UUID('{ba4f7e02-a5d1-4c60-9a95-de51142aa51a}'), uuid.UUID('{cfca912b-eaaa-449f-8162-682289e23e4b}')}, {uuid.UUID('{cfca912b-eaaa-449f-8162-682289e23e4b}'), uuid.UUID('{d68a329e-caac-4114-8e0b-e3be895fb538}')})
    )
    db.execute(
        '''
        insert into mt_api.message (user_id, username, email, pub_date, text, whom_id, who_id)
        values (%s, %s, %s, %s, %s, %s, %s)
        ''',
        (uuid.UUID('{c405ae0d-b7f1-44dd-8c95-f442fea668ab}'), 'bob', 'bob@gmail.com', 1518409808, 'testing from bob', {uuid.UUID('{ba4f7e02-a5d1-4c60-9a95-de51142aa51a}'), uuid.UUID('{cfca912b-eaaa-449f-8162-682289e23e4b}')}, {uuid.UUID('{cfca912b-eaaa-449f-8162-682289e23e4b}'), uuid.UUID('{d68a329e-caac-4114-8e0b-e3be895fb538}')})
    )
    db.execute(
        '''
        insert into mt_api.message (user_id, username, email, pub_date, text, who_id)
        values (%s, %s, %s, %s, %s, %s)
        ''',
        (uuid.UUID('{cfca912b-eaaa-449f-8162-682289e23e4b}'), 'eve', 'eve@gmail.com', 1518409719, 'backend practice eve', {uuid.UUID('{d68a329e-caac-4114-8e0b-e3be895fb538}')})
    )
    db.execute(
        '''
        insert into mt_api.message (user_id, username, email, pub_date, text, whom_id)
        values (%s, %s, %s, %s, %s, %s)
        ''',
        (uuid.UUID('{d68a329e-caac-4114-8e0b-e3be895fb538}'), 'smith', 'smith@gmail.com', 1518409764, 'hi from smith', {uuid.UUID('{ba4f7e02-a5d1-4c60-9a95-de51142aa51a}'), uuid.UUID('{c405ae0d-b7f1-44dd-8c95-f442fea668ab}')})
    )


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
        if request.method == 'GET':
            user = query_db('''select * from user where username = ?''', [data['username']], one=True)
            print user
            if user:
                user = dict(user)
                return jsonify(user)
            return jsonify(user)
    if 'user_id' in data:
        if request.method == 'GET':
            user = query_db('''select * from user where user_id = ?''', [uuid.UUID(data['user_id'])], one=True)
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
            whom_set = query_db('''select whom_id from message where user_id = ? limit 1''', [user_id])
            print "whom_set"
            print whom_set
            whom_id_set = []
            if whom_set:
                if 'whom_id' in whom_set[0]:
                    for whom_id in whom_set[0]['whom_id']:
                        whom_id_set.append(whom_id)
            print "whom_id_set"
            print whom_id_set
            who_set = query_db('''select who_id from message where user_id = ? limit 1''', [user_id])
            print "who_set"
            print who_set
            who_id_set = []
            if who_set:
                if 'who_id' in who_set[0]:
                    for who_id in who_set[0]['who_id']:
                        print who_id
                        who_id_set.append(who_id)
            print "who_id_set"
            print who_id_set
            query_db('''insert into message (username, user_id, email, pub_date, text, whom_id, who_id)
            values (?, ?, ?, ?, ?, ?, ?)''', [data["username"], uuid.UUID(data["user_id"]), data['email'],data['pub_date'], data["text"], whom_id_set, who_id_set])
            print 'Your message was recorded'
        return jsonify(data)
    return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')


@app.route('/users/<username>/messages', methods=['GET', 'POST', 'PUT', 'DELETE'])
def get_user_messages(username):
    """Displays a user's tweets"""
    profile_user = query_db('select * from message where username = ?',[username], one=True)
    if profile_user is None:
        return make_error(404, 'Not Found', 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.')
    data = request.get_json()
    user_id = get_user_id(username)
    if request.method == 'GET':
        if username in data:
            messages = query_db('''select username, user_id, pub_date, text, email from message where username = ? limit ?''', [username ,PER_PAGE])

            whom_id_set = query_db('''select whom_id from message where user_id = ?''', [user_id])
            print whom_id_set[0]
            print 'break here'

            if whom_id_set[0]['whom_id']:
                if 'whom_id'in whom_id_set[0]:
                    for whom_id in whom_id_set[0]['whom_id']:
                        print whom_id
                        message = query_db('''select text, username, email, pub_date from message where user_id = ? limit ?''', [whom_id, PER_PAGE])
                        for elem in message:
                            messages.append(elem)
        else:
            messages = query_db('''select username, user_id, pub_date, text, email from message where username = ? limit ?''', [username ,PER_PAGE])


        for message in messages:
            if message['text'] is None:
                messages.remove(message)
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

    whom_set = query_db('''select whom_id from message where user_id = ? limit 1''', [uuid.UUID(data['user_id'])], one=True)
    print whom_set
    whom_id_set = []
    if whom_set:
        if 'whom_id' in whom_set:
            if whom_set['whom_id']:
                for whom_id in whom_set['whom_id']:
                    whom_id_set.append(whom_id)
    if whom_id_set:
        for whom_id in whom_id_set:
            print whom_id
            if uuid.UUID(data['profile_user_id']) == whom_id:
                print 'break'
                return jsonify(1)

    return jsonify(None)


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
        date_set = query_db('''select pub_date from message where user_id = ?''', [uuid.UUID(user_id)])
        pub_date = []
        for date in date_set:
            pub_date.append(date['pub_date'])
        db = get_db()
        if date_set:
            for current in pub_date:
                db.execute('''update message set whom_id = whom_id + { %s } where username = %s and user_id = %s and email = %s and pub_date in (%s)''', (uuid.UUID(data['whom_id']), data['username'], uuid.UUID(user_id), data['email'], int(current)))
        else:
            query_db('''insert into message (username, user_id, email, pub_date, whom_id) values (?, ?, ?, ?, ?)''', [data['username'], uuid.UUID(user_id), data['email'], data['pub_date'], {uuid.UUID(data['whom_id'])}])

        print 'You are following user has user_id ', data['whom_id']
    print data
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
        date_set = query_db('''select pub_date from message where user_id = ?''', [uuid.UUID(user_id)])
        pub_date = []
        for date in date_set:
            pub_date.append(date['pub_date'])
        db = get_db()
        if date_set:
            for current in pub_date:
                db.execute('''update message set whom_id = whom_id - { %s } where username = %s and user_id = %s and email = %s and pub_date in (%s)''', (uuid.UUID(data['whom_id']), data['username'], uuid.UUID(user_id), data['email'], int(current)))
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
        print uuid.uuid1()
        query_db('''insert into user (username, user_id, email, pw_hash) values(?, ?, ?, ?)''', [data['username'], uuid.uuid1(), data['email'], data['pw_hash']])

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

        user = query_db('''select text, username, email, pub_date from message where user_id = ? limit ?''', [uuid.UUID(data['user_id']), PER_PAGE])
        whom_id_set = query_db('''select whom_id from message where user_id = ?''', [uuid.UUID(data['user_id'])])

        if whom_id_set:
            if whom_id_set[0]['whom_id']:
                if 'whom_id' in whom_id_set[0]:
                    for whom_id in whom_id_set[0]['whom_id']:
                        print whom_id
                        message = query_db('''select text, username, email, pub_date from message where user_id = ? limit ?''', [whom_id, PER_PAGE])
                        for elem in message:
                            user.append(elem)
    else:
        messages = query_db('''select text, username, email, pub_date from message limit ?''', [PER_PAGE])

    for elem in user:
        if elem['text'] is None:
            user.remove(elem)
    return jsonify(user)


@app.route('/timeline', methods=['POST', 'GET', 'PUT', 'DELETE'])
def public_time_line():
    '''display latest messages of all users.'''
    if request.method != 'GET':
        return make_error(405, 'Method Not Allowed', 'The method is not allowed for the requested URL.')

    messages = query_db('''select text, username, email, pub_date from message limit ?''', [PER_PAGE])

    for message in messages:
        if message['text'] is None:
            messages.remove(message)

    return jsonify(messages)


if __name__ == '__main__':
    app.run(debug=True)
