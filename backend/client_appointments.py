from flask import (Blueprint, jsonify, request, session,
                    render_template, url_for, redirect)
from db import get_psql_conn
import pandas as pd


client_appointments = Blueprint("client_appointments", __name__)

###### serving pages ######
@client_appointments.get('/client-appointments')
def serve_client_appointment_page():
    if not session.get("login"):
        return redirect("/login")
    return render_template("client-appointments.html")

@client_appointments.get('/client-appointments/make')
def serve_client_appointment_make_page():
    if not session.get("login"):
        return redirect("/login")
    return render_template("client-appointments-make.html")


###### api calls ######
@client_appointments.post('/get_user_appointments')
def get_user_appointments():
    status = "'" + request.json['status'] + "'"
    
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT appointment_id, datetime, created_at,
                S.service_name, B.branch_name, D.name
            FROM APPOINTMENT AS AP
                JOIN SERVICE AS S ON AP.for_service = S.service_id
                JOIN BRANCH AS B ON AP.at_branch = B.branch_id
                JOIN DOCTOR AS D ON AP.chosen_doctor = D.doctor_id
            WHERE made_by_user = {session.get("user_id")}
                AND status = {status}
            ORDER BY datetime DESC, created_at DESC
            LIMIT 10
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        if len(results) == 0:  # user has no pets
            return jsonify({'tableHTML': "<p>No appointments found.</p>"})
        
        # convert query result into dataframe and return
        apps_df = pd.DataFrame(results, columns=[
            "appointment_id", "appointment time", "creation time", "service",
            "branch", "doctor"
        ])
        return jsonify({
            'tableHTML': apps_df.to_html(index=False)
        })