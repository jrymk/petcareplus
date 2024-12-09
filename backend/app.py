import os
from flask import Flask, render_template, session, redirect
from db import init_db_conn

from login import login
from client_mypets import client_mypets


# Global Flask app (SUBJECT TO CHANGE)
app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
app.register_blueprint(login)
app.register_blueprint(client_mypets)


# Initialize the app and connect to the database.
def init_app():
    init_db_conn()
    app.secret_key = os.urandom(32)  # session key


# serve homepage
@app.route('/')
def serve_homepage():
    if session.get("login"):
        if session.get("role") == "doctor":
            return render_template("doctor-home.html",
                                   username=session.get("username"))
        else:
           return render_template("client-home.html",
                                  username=session.get("username"))
    else:
        return redirect("/login")  # redirect to login page if not logged in


if __name__ == '__main__':
    init_app()
    app.run()