import os
from flask import Flask, render_template, session, redirect
from db import init_db_conn

from login import login
from client_mypets import client_mypets
from client_appointments import client_appointments
from client_visitrecords import client_visitrecords
from client_bills import client_bills
from doctor_schedule import doctor_schedule
from doctor_appointment import doctor_appointment
from doctor_records import doctor_records
from utils import utils


# Global Flask app (SUBJECT TO CHANGE)
app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
app.register_blueprint(login)
app.register_blueprint(client_mypets)
app.register_blueprint(client_appointments)
app.register_blueprint(client_visitrecords)
app.register_blueprint(client_bills)
app.register_blueprint(doctor_schedule)
app.register_blueprint(doctor_appointment)
app.register_blueprint(doctor_records)
app.register_blueprint(utils)


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
    app.run(debug=True)