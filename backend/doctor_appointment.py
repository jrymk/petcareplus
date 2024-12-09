import datetime
from flask import (Blueprint, jsonify, request, session,
                    render_template, url_for, redirect)
from db import get_psql_conn
import pandas as pd


doctor_appointment = Blueprint("doctor_appointment", __name__)

@doctor_appointment.get('/doctor-appointment')
def serve_doctor_home():
    if not session.get("login"):
        return redirect("/login")
    
    appointment_id = request.args.get('appointment_id')
    return render_template("doctor-appointment.html", appointment_id=appointment_id)
