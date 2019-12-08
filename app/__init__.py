# Import flask and template operators
from flask import Flask, render_template, redirect, url_for, session
import os
import shutil


# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
        return render_template('/errors/404.html'), 404

@app.route('/', methods=['GET', 'POST'])
def hello():
    if 'token' in session and os.path.exists(f'app/storage/{session["token"]}'):
        return redirect(url_for('aggregator.document'))
    return render_template('hello.html')

@app.route('/new', methods=['GET', 'POST'])
def new():
    token = session.pop('token')
    shutil.rmtree(f'app/storage/{token}')
    return redirect(url_for('hello'))

# Import a module / component using its blueprint handler variable (mod_auth)
from app.aggregator.routes import aggregator

# Register blueprint(s)
app.register_blueprint(aggregator)

