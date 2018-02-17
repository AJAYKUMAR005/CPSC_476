import minitwit
import time
from flask import Flask, request, jsonify, g, json, abort
from flask_basicauth import BasicAuth

app = Flask(__name__)

# app.config['BASIC_AUTH_USERNAME'] = 'john'
# app.config['BASIC_AUTH_PASSWORD'] = 'matrix'

basic_auth = BasicAuth(app)

def get_credentials(username):
    user_name = minitwit.query_db('''select username from user where user.username = ?''', [username], one=True)
    pw_hash = minitwit.query_db('''select pw_hash from user where user.username = ?''', [username], one=True)
    app.config['BASIC_AUTH_USERNAME'] = user_name[0]
    app.config['BASIC_AUTH_PASSWORD'] = pw_hash[0]

def populate_db():
    """Re-populates the database with test data"""
    db = minitwit.get_db()
    with app.open_resource('population.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def make_error(status_code, message, reason):
    response = jsonify({
        "status" : status_code,
        "message" : message,
        "reason" : reason
    })
    return response

@app.cli.command('populatedb')
def populatedb_command():
    """Inputs data in database tables."""
    populate_db()
    print('Database population is completed.')

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

@app.route('/users/<username>', methods=['GET'])
def user_info(username):
    """Gets user's information"""
    if request.method == 'GET':
        user = minitwit.query_db('''
        select * from user
        where user.username = ?''',
        [username])
        print user
        user = map(dict, user)
    return jsonify(user)

@app.route('/users/<username>/add_message', methods=['POST'])
def add_message(username):
    """Inserts a new message from current <user_id>"""
    data = request.get_json()
    user_id = minitwit.get_user_id(username)
    get_credentials(username)
    print basic_auth.check_credentials(data["username"], data["pw_hash"])
    if not basic_auth.check_credentials(data["username"], data["pw_hash"]):
        return make_error(401, 'Unauthorized', 'Correct username and password are required.')
    if data:
        db = minitwit.get_db()
        db.execute('''insert into message (author_id, text, pub_date)
        values (?, ?, ?)''', [user_id, data["text"], int(time.time())])
        db.commit()
    return jsonify(data)

@app.route('/users/<username>/messages', methods=['GET'])
def get_user_messages(username):
    """Displays a user's tweets"""
    profile_user = minitwit.query_db('select * from user where username = ?',[username], one=True)
    print profile_user
    if profile_user is None:
        return make_error(404, 'Not Found', 'The requested resource could not be found.')
    followed = False
    messages = minitwit.query_db('''select message.*, user.* from message, user where user.user_id = message.author_id and user.user_id = ? order by message.pub_date desc limit ?''',
    [profile_user['user_id'], minitwit.PER_PAGE])
    messages = map(dict, messages)
    return jsonify(messages)

# @app.route('/users/<username>/follow', methods=['POST'])
# def add_follow_user(username):
#     data = request.get_json()
#     if


if __name__ == '__main__':
    app.run(debug=True)
