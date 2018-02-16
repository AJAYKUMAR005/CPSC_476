import minitwit
import time
from flask import Flask, request, jsonify, g, json

app = Flask(__name__)

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
    """Gets user's information""""
    if request.method == 'GET':
        user = minitwit.query_db('''
        select * from user
        where user.username = ?''',
        [username])
        print user
        user = map(dict, user)
    return jsonify(user)

@app.route('/users/<user_id>/add_message', methods=['POST'])
def add_message(user_id):
    """Inserts a new message from current <user_id>"""
    print (request.is_json)
    data = request.get_json()
    print data
    if data:
        db = minitwit.get_db()
        db.execute('''insert into message (author_id, text, pub_date)
        values (?, ?, ?)''', [data["author_id"], data["text"], int(time.time())])
        db.commit()
    return jsonify(data)

@app.route('/users/<username>/', methods=['GET'])
def user_timeline(username):
    """Displays a user's tweets"""
    profile_user = query_db('select * from user where username = ?',
                            [username], one=True)


if __name__ == '__main__':
    app.run(debug=True)
