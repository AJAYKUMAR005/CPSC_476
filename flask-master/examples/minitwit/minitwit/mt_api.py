import minitwit
from flask import Flask, request, jsonify, g

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

if __name__ == '__main__':
    app.run(debug=True)
