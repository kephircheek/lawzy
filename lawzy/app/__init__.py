# Import flask and template operators
import os
import shutil

from flask import Flask, redirect, render_template, session, url_for

from lawzy.config import UPLOAD_FOLDER

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object("lawzy.config")


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template("/errors/404.html"), 404


@app.route("/", methods=["GET", "POST"])
def hello():
    if "token" in session and os.path.exists(f'{UPLOAD_FOLDER}/{session["token"]}'):
        return redirect(url_for("aggregator.document"))
    return render_template("hello.html")


@app.route("/new", methods=["GET", "POST"])
def new():
    token = session.pop("token")
    shutil.rmtree(f"{UPLOAD_FOLDER}/{token}")
    session.clear()
    return redirect(url_for("hello"))


# Import a module / component using its blueprint handler variable (mod_auth)
from lawzy.app.aggregator.routes import aggregator

# Register blueprint(s)
app.register_blueprint(aggregator)
