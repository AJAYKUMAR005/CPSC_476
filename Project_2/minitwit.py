# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: © 2010 by the Pallets team.
    :license: BSD, see LICENSE for more details.
"""
import requests
import mt_api
import time
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash


SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

# create our little application :)
app = Flask('minitwit')
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'https://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        url = 'http://localhost:8080/users/' + str(session['user_id'])
        payload = {'user_id': session['user_id']}
        r = requests.get(url, json=payload)
        g.user = r.json()


@app.route('/')
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.user:
        return redirect(url_for('public_timeline'))
    else:
        url = 'http://localhost:8080/users'
        payload = {'user_id': session['user_id'], 'pw_hash': session['pw_hash'], 'username': session['username']}
        r = requests.get(url, json=payload)
        return render_template('timeline.html', messages=r.json())


@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    payload = {}
    url = 'http://localhost:8080/timeline'
    r = requests.get(url, json=payload)
    return render_template('timeline.html', messages=r.json())


@app.route('/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    payload = {'username': username}
    url = 'http://localhost:8080/users/' + username
    r = requests.get(url, json=payload)
    profile_user = r.json()
    if profile_user is None:
        abort(404)
    followed = False
    if g.user:
        payload = {'user_id': session['user_id'], 'pw_hash': session['pw_hash'], 'username': session['username'], 'profile_user_id': profile_user['user_id']}
        url = 'http://localhost:8080/users/' + str(session['user_id']) + '/follow'
        r = requests.get(url, json=payload)
        followed = r.json() is not None
    payload = {'profile_user_id': profile_user['user_id']}
    url = 'http://localhost:8080/users/' + profile_user['username'] + '/messages'
    r = requests.get(url, json=payload)
    return render_template('timeline.html', messages = r.json(), followed=followed, profile_user=profile_user)

@app.route('/<username>/follow')
def follow_user(username):
    """Adds the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = mt_api.get_user_id(username)
    if whom_id is None:
        abort(404)
    payload = {'user_id': session['user_id'], 'pw_hash': session['pw_hash'], 'username': session['username'], 'whom_id': whom_id}
    url = 'http://localhost:8080/users/' + str(session['user_id']) + '/add_follow'
    r = requests.post(url, json=payload)
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = mt_api.get_user_id(username)
    if whom_id is None:
        abort(404)
    payload = {'user_id': session['user_id'], 'pw_hash': session['pw_hash'], 'username': session['username'], 'whom_id': whom_id}
    url = 'http://localhost:8080/users/' + str(session['user_id']) + '/unfollow'
    r = requests.delete(url, json=payload)
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/add_message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        payload = {'author_id': session['user_id'], 'pw_hash': session['pw_hash'], 'username': session['username'], 'text': request.form['text'], 'pub_date': int(time.time())}
        url = 'http://localhost:8080/users/' + session['username'] + '/add_message'
        r = requests.post(url, json=payload)
        flash('Your message was recorded')
    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        payload = {'username': request.form['username']}
        print request.form['username']
        print payload
        url = 'http://localhost:8080/users/' + request.form['username']
        r = requests.get(url, json=payload)
        user = r.json()
        print user
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user['user_id']
            session['pw_hash'] = user['pw_hash']
            session['username'] = user['username']
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif mt_api.get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            payload = {'username': request.form['username'], 'email': request.form['email'], 'pw_hash': generate_password_hash(request.form['password'])}
            print payload
            url = 'http://localhost:8080/users/Sign_up'
            r = requests.post(url, json=payload)
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_timeline'))


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url
